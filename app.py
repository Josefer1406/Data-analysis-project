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

from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

# =========================
# API
# =========================
@app.route("/")
def home():
    return "🚀 BOT CUANT - MODO ENTRENAMIENTO"

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

# =========================
# BOT
# =========================
def run_bot():

    print("🤖 BOT EN MODO ENTRENAMIENTO (SIN FILTRO)")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            ranking = []

            # =========================
            # SCANNER
            # =========================
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

            # =========================
            # ORDENAR POR PROBABILIDAD (ML)
            # =========================
            ranking.sort(key=lambda x: x[4], reverse=True)

            # =========================
            # TOMAR TOP
            # =========================
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRE DE POSICIONES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                try:
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

                        print(f"🔴 SELL {symbol} | PnL: {pnl}")

                except Exception as e:
                    print(f"Error cierre {symbol}: {e}")

            # =========================
            # APERTURA (MENOS ESTRICTO)
            # =========================
            for symbol, score, precio, decision, prob in top:
                try:
                    # 🔥 MODO ENTRENAMIENTO: menos filtro
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

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print("⏳ Generando datos...\n")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR GENERAL: {e}")
            time.sleep(10)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)