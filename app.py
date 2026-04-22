from flask import Flask, jsonify
import threading
import time
import config

from services_v3.data_engine import obtener_multi_timeframe, obtener_universo
from services_v3.features import calcular_features
from services_v3.market_regime import detectar_regimen
from services_v3.ranker import calcular_score
from services_v3.selector import seleccionar_activos
from services_v3.rotation import evaluar_rotacion

from ml_v3.model import ml_model
from portfolio import portfolio

app = Flask(__name__)


def tipo_trade(score):
    if score > 0.7:
        return "elite"
    return "normal"


def bot():

    print("🚀 BOT QUANT V3 ACTIVADO")

    while True:
        try:

            universo = obtener_universo()

            candidatos = []
            precios_dict = {}

            features_list = []

            # =========================
            # DATA + FEATURES
            # =========================
            for symbol in universo:

                data = obtener_multi_timeframe(symbol)

                if data is None:
                    continue

                features = calcular_features(data)

                precio = data["5m"]["close"].iloc[-1]

                precios_dict[symbol] = data["5m"]["close"].values

                # ML
                ml_prob = ml_model.predict(features)

                score = calcular_score(features, ml_prob)

                features_list.append(features)

                candidatos.append({
                    "symbol": symbol,
                    "precio": precio,
                    "features": features,
                    "score": score
                })

            # =========================
            # MERCADO
            # =========================
            mercado = detectar_regimen(features_list)

            # =========================
            # SELECCIÓN
            # =========================
            seleccionados = seleccionar_activos(
                candidatos,
                precios_dict,
                config.MAX_POSICIONES
            )

            # =========================
            # ROTACIÓN
            # =========================
            rotacion = evaluar_rotacion(portfolio, seleccionados)

            if rotacion:
                portfolio.cerrar(
                    rotacion["salir"],
                    precios_dict[rotacion["salir"]][-1],
                    0
                )

                nuevo = rotacion["entrar"]

                portfolio.comprar(
                    nuevo["symbol"],
                    nuevo["precio"],
                    nuevo["features"],
                    nuevo["score"],
                    tipo_trade(nuevo["score"])
                )

            # =========================
            # LLENAR PORTAFOLIO
            # =========================
            for asset in seleccionados:

                if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                    break

                portfolio.comprar(
                    asset["symbol"],
                    asset["precio"],
                    asset["features"],
                    asset["score"],
                    tipo_trade(asset["score"])
                )

            # =========================
            # UPDATE
            # =========================
            precios_actuales = {
                s: precios_dict[s][-1] for s in precios_dict
            }

            portfolio.actualizar(precios_actuales)

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"🌍 Mercado: {mercado}")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(5)


@app.route("/data")
def data():
    return jsonify(portfolio.data())


if __name__ == "__main__":
    threading.Thread(target=bot).start()
    app.run(host="0.0.0.0", port=8080)