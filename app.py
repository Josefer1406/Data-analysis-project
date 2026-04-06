from flask import Flask, jsonify
import threading
import time
import datetime
import os

import config
import portfolio

from services.scanner import analizar
from core.risk import calcular_size
from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 BOT CUANT - ENTRENAMIENTO ACTIVO"

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

    print("🤖 BOT ENTRENANDO (ESTABLE)")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            ranking = []

            for symbol in config.CRYPTOS:
                try:
                    score, precio, decision, prob = analizar(symbol)
                    ranking.append((symbol, score, precio, decision, prob))
                except Exception as e:
                    print(f"Error analizando {symbol}: {e}")

            if not ranking:
                print("⚠️ No hay datos")
                time.sleep(config.CYCLE_TIME)
                continue

            # ordenar por ML
            ranking.sort(key=lambda x: x[4], reverse=True)

            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                precio_actual = next(
                    (p for s, sc, p, d, pr in ranking if s == symbol),
                    None
                )

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
            # APERTURAS
            # =========================
            for symbol, score, precio, decision, prob in top:

                if prob > 0.55:

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

                        print(f"🟢 BUY {symbol} | prob: {round(prob,2)}")

            print(f"💰 Capital: {portfolio.capital}")
            print("⏳ Entrenando...\n")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))