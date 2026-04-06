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

# =========================
# FLASK
# =========================
app = Flask(__name__)

# =========================
# RUTAS API
# =========================
@app.route("/")
def home():
    return "🚀 BOT CUANT ACTIVO - API OK"

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
# BOT LOOP
# =========================
def run_bot():

    print("🤖 BOT INICIADO (MODO FORZADO)")

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
                    score, precio, decision = analizar(symbol)
                    ranking.append((symbol, score, precio, decision))
                except Exception as e:
                    print(f"Error analizando {symbol}: {e}")

            if not ranking:
                print("⚠️ No hay datos del scanner")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # FORZAR COMPRAS (DEBUG)
            # =========================
            for symbol, score, precio, decision in ranking:
                try:
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

                        print(f"🟢 BUY FORZADO {symbol}")

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            print(f"💰 Capital: {portfolio.capital}")
            print("⏳ Esperando siguiente ciclo...\n")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR GENERAL: {e}")
            time.sleep(10)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)