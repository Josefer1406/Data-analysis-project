from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# SCORE
# =========================
def score(asset):
    return (asset["prob"] * 0.7) + ((asset["score"] / 3) * 0.3)


# =========================
# CLASIFICACIÓN
# =========================
def clasificar(asset, prob_min):

    if asset["prob"] >= prob_min + 0.1 and asset["score"] >= 2:
        return "elite"

    if asset["prob"] >= prob_min and asset["score"] >= 1:
        return "normal"

    return None


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT IA RENTABLE ACTIVADO")

    while True:
        try:

            print("\n🔎 Analizando mercado...")

            candidatos = []
            precios = {}

            prob_min = portfolio.ajustar_filtro()

            # =========================
            # SCAN
            # =========================
            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None:
                    continue

                precios[symbol] = data["precio"]

                tipo = clasificar(data, prob_min)

                if tipo is None:
                    continue

                data["score_final"] = score(data)
                data["tipo"] = tipo

                candidatos.append(data)

            # =========================
            portfolio.actualizar(precios)

            candidatos = sorted(candidatos, key=lambda x: x["score_final"], reverse=True)

            # =========================
            # ROTACIÓN INTELIGENTE REAL
            # =========================
            if portfolio.posiciones and candidatos:

                mejor = candidatos[0]

                peor_symbol = None
                peor_score = 999

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_score:
                        peor_score = pos["prob"]
                        peor_symbol = s

                if mejor["prob"] > peor_score + config.ROTACION_UMBRAL:
                    print(f"🔄 ROTACIÓN REAL {peor_symbol} → {mejor['symbol']}")

                    portfolio.cerrar(peor_symbol, precios.get(peor_symbol, 0), 0)

                    portfolio.comprar(
                        mejor["symbol"],
                        mejor["precio"],
                        mejor["prob"],
                        mejor["tipo"]
                    )

            # =========================
            # LLENAR PORTAFOLIO
            # =========================
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

            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📈 Candidatos: {len(candidatos)}")
            print(f"🧠 IA Win/Loss: {portfolio.win}/{portfolio.loss}")
            print(f"🎯 Prob mínima actual: {prob_min}")

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