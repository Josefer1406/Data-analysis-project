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
# API
# =========================
@app.route("/")
def home():
    return "🚀 BOT CUANT PROFESIONAL ACTIVO"

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

    print("🤖 BOT PROFESIONAL INICIADO")

    portfolio.cargar_estado()
    crear_tablas()

    ciclos = 0

    while True:
        try:
            ciclos += 1

            params = adaptive.ajustar_parametros()
            MIN_SCORE = params.get("MIN_SCORE", 2)
            config.RIESGO_POR_TRADE = params.get("RIESGO", 0.02)

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
                print("⚠️ No hay datos")
                time.sleep(config.CYCLE_TIME)
                continue

            ranking.sort(key=lambda x: x[1], reverse=True)
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRE
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                try:
                    precio_actual = next(
                        (p for s, sc, p, d in ranking if s == symbol),
                        None
                    )

                    if precio_actual is None:
                        continue

                    if portfolio.evaluar_salida(symbol, precio_actual):

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
            # APERTURA (YA NO FORZADO)
            # =========================
            for symbol, score, precio, decision in top:
                try:
                    if decision == "BUY" and score >= MIN_SCORE:

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

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print("⏳ Esperando...\n")

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