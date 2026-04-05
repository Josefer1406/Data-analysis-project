from flask import Flask, jsonify
import threading
import time
import pandas as pd
import os
import datetime

import config
import portfolio
import adaptive

from filters.market_filter import mercado_favorable
from services.scanner import analizar
from core.risk import calcular_size

from database import crear_tablas, insertar_trade, obtener_trades
from ml.train import entrenar

# =========================
# FLASK
# =========================
app = Flask(__name__)

# =========================
# API
# =========================
@app.route("/")
def home():
    return "BOT + ML + DB ACTIVO 🚀"

@app.route("/data")
def data():
    rows = obtener_trades()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "fecha": r[1],
            "symbol": r[2],
            "tipo": r[3],
            "precio": r[4],
            "size": r[5],
            "pnl": r[6],
            "capital": r[7]
        })

    return jsonify(data)

# =========================
# BOT LOOP
# =========================
def run_bot():

    print("🤖 BOT ML INICIADO")

    portfolio.cargar_estado()
    crear_tablas()

    ciclos = 0

    while True:
        try:
            ciclos += 1

            estado_mercado = mercado_favorable()
            params = adaptive.ajustar_parametros()

            MIN_SCORE = params["MIN_SCORE"]
            config.RIESGO_POR_TRADE = params["RIESGO"]

            ranking = []

            for symbol in config.CRYPTOS:
                try:
                    score, precio = analizar(symbol)
                    ranking.append((symbol, score, precio))
                except Exception as e:
                    print(f"Error {symbol}: {e}")

            if not ranking:
                time.sleep(config.CYCLE_TIME)
                continue

            ranking.sort(key=lambda x: x[1], reverse=True)
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                precio_actual = next((p for s, sc, p in ranking if s == symbol), None)

                if precio_actual and portfolio.evaluar_salida(symbol, precio_actual):

                    size = portfolio.posiciones[symbol]["size"]
                    pnl = portfolio.cerrar_posicion(symbol, precio_actual)

                    insertar_trade(
                        datetime.datetime.now(),
                        symbol,
                        "SELL",
                        precio_actual,
                        size,
                        pnl,
                        portfolio.capital
                    )

            # =========================
            # APERTURAS
            # =========================
            for symbol, score, precio in top:

                if score >= MIN_SCORE:

                    size = calcular_size(precio)

                    if portfolio.abrir_posicion(symbol, precio, size):

                        insertar_trade(
                            datetime.datetime.now(),
                            symbol,
                            "BUY",
                            precio,
                            size,
                            0,
                            portfolio.capital
                        )

            # =========================
            # 🔥 AUTO-ML
            # =========================
            if ciclos % 10 == 0:
                print("🧠 Reentrenando modelo...")
                entrenar()

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)