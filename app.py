from flask import Flask, jsonify
import threading
import time
import datetime
import os

import config
import portfolio
import adaptive

from services.scanner import analizar
from core.risk import calcular_size
from filters.market_filter import mercado_favorable

from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 BOT CUANT OPTIMIZADO"

@app.route("/data")
def data():
    rows = obtener_trades()

    return jsonify([
        {
            "fecha": r[1],
            "symbol": r[2],
            "tipo": r[3],
            "precio": r[4],
            "size": r[5],
            "pnl": r[6],
            "capital": r[7]
        } for r in rows
    ])

def run_bot():

    print("🤖 BOT OPTIMIZADO INICIADO")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            # =========================
            # FILTRO DE MERCADO
            # =========================
            if not mercado_favorable():
                print("🚫 Mercado no favorable, no operar")
                time.sleep(config.CYCLE_TIME)
                continue

            ranking = []

            for symbol in config.CRYPTOS:
                try:
                    score, precio, decision = analizar(symbol)
                    ranking.append((symbol, score, precio, decision))
                except Exception as e:
                    print(f"Error {symbol}: {e}")

            ranking.sort(key=lambda x: x[1], reverse=True)

            # =========================
            # SOLO TOP 2 (MENOS TRADES)
            # =========================
            top = ranking[:2]

            # =========================
            # CIERRES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                precio_actual = next((p for s, sc, p, d in ranking if s == symbol), None)

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

                    print(f"🔴 SELL {symbol}")

            # =========================
            # APERTURAS (MUY SELECTIVO)
            # =========================
            for symbol, score, precio, decision in top:

                if decision == "BUY":

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

                        print(f"🟢 BUY {symbol}")

            print(f"💰 Capital: {portfolio.capital}")
            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))