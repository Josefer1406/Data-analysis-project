from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)

def bot():

    print("🚀 BOT INSTITUCIONAL INICIADO")

    while True:
        try:
            print("\n🔎 Analizando mercado...")

            ranking = []
            precios = {}

            # =========================
            # SCAN
            # =========================
            for symbol in config.CRYPTOS:
                score, precio, _, prob = analizar(symbol)
                ranking.append((symbol, score, prob, precio))
                precios[symbol] = precio

            # =========================
            # GESTIÓN POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # SELECCIÓN TOP (CLAVE)
            # =========================
            ranking = sorted(ranking, key=lambda x: x[2], reverse=True)

            top = ranking[:2]  # 🔥 SOLO TOP 2

            # =========================
            # EJECUCIÓN
            # =========================
            for symbol, score, prob, precio in top:
                portfolio.comprar(symbol, precio, prob)

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")

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