from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio
from ia_model import score_ia

app = Flask(__name__)


def score(asset):
    return (asset["prob"] * 0.7) + ((asset["score"] / 3) * 0.3)


def tipo_trade(asset):
    if asset["prob"] >= 0.85:
        return "elite"
    return "normal"


def detectar_mercado(candidatos):

    if not candidatos:
        return "neutral"

    avg = sum(c["prob"] for c in candidatos) / len(candidatos)

    if avg > 0.75:
        return "bull"

    if avg < 0.6:
        return "bear"

    return "lateral"


def bot():

    print("🚀 BOT IA INSTITUCIONAL REAL")

    while True:
        try:

            print("\n🔎 Analizando mercado...")

            candidatos = []
            precios = {}

            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None:
                    continue

                precios[symbol] = data["precio"]

                data["score_final"] = score(data)
                data["tipo"] = tipo_trade(data)

                candidatos.append(data)

            portfolio.actualizar(precios)

            mercado = detectar_mercado(candidatos)

            filtrados = []

            for asset in candidatos:

                ia = score_ia({
                    "prob": asset["prob"],
                    "tipo": asset["tipo"]
                })

                if mercado == "bull" and ia > 0.45:
                    filtrados.append(asset)

                elif mercado == "lateral" and ia > 0.55:
                    filtrados.append(asset)

                elif mercado == "bear" and ia > 0.65:
                    filtrados.append(asset)

            candidatos = sorted(filtrados, key=lambda x: x["score_final"], reverse=True)

            # ROTACIÓN
            if portfolio.posiciones and candidatos:

                mejor = candidatos[0]
                peor_symbol, peor_prob = portfolio.peor_posicion()

                if mejor["prob"] > peor_prob + config.ROTACION_UMBRAL:
                    print(f"🔄 ROTACIÓN {peor_symbol} → {mejor['symbol']}")

                    portfolio.cerrar(peor_symbol, precios.get(peor_symbol, 0), 0)

                    portfolio.comprar(
                        mejor["symbol"],
                        mejor["precio"],
                        mejor["prob"],
                        mejor["tipo"]
                    )

            # LLENAR PORTAFOLIO
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios > 0:

                print(f"📈 Llenando {espacios} posiciones")

                for asset in candidatos:

                    if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                        break

                    portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"],
                        asset["tipo"]
                    )

            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📈 Candidatos: {len(candidatos)}")
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