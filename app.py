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

# =========================
# FLASK
# =========================
app = Flask(__name__)

# =========================
# API
# =========================
@app.route("/")
def home():
    return "BOT + API + DB ACTIVO ✅"

@app.route("/data")
def data():
    try:
        rows = obtener_trades()

        # convertir a formato JSON
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

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# BOT LOOP
# =========================
def run_bot():

    print("🤖 BOT PROFESIONAL INICIADO")

    portfolio.cargar_estado()
    crear_tablas()  # 🔥 crea DB si no existe

    while True:
        try:
            estado_mercado = mercado_favorable()

            params = adaptive.ajustar_parametros()

            MIN_SCORE = params["MIN_SCORE"]
            config.RIESGO_POR_TRADE = params["RIESGO"]

            print(f"🧠 MIN_SCORE: {MIN_SCORE} | Riesgo: {config.RIESGO_POR_TRADE}")

            ranking = []

            for symbol in config.CRYPTOS:
                try:
                    score, precio = analizar(symbol)
                    ranking.append((symbol, score, precio))
                except Exception as e:
                    print(f"Error analizando {symbol}: {e}")

            if not ranking:
                time.sleep(config.CYCLE_TIME)
                continue

            ranking.sort(key=lambda x: x[1], reverse=True)
            top_cryptos = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRE DE POSICIONES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                try:
                    precio_actual = next(
                        (p for s, sc, p in ranking if s == symbol),
                        None
                    )

                    if precio_actual is None:
                        continue

                    if portfolio.evaluar_salida(symbol, precio_actual):

                        size = portfolio.posiciones[symbol]["size"]
                        pnl = portfolio.cerrar_posicion(symbol, precio_actual)

                        # 🔥 GUARDAR EN DB
                        insertar_trade(
                            datetime.datetime.now(),
                            symbol,
                            "SELL",
                            precio_actual,
                            size,
                            pnl,
                            portfolio.capital
                        )

                        print(f"🔴 Cierre {symbol} | PnL: {pnl}")

                except Exception as e:
                    print(f"Error cierre {symbol}: {e}")

            # =========================
            # APERTURA DE POSICIONES
            # =========================
            for symbol, score, precio in top_cryptos:
                try:
                    if score >= MIN_SCORE:

                        size = calcular_size(precio)

                        if portfolio.abrir_posicion(symbol, precio, size):

                            # 🔥 GUARDAR EN DB
                            insertar_trade(
                                datetime.datetime.now(),
                                symbol,
                                "BUY",
                                precio,
                                size,
                                0,
                                portfolio.capital
                            )

                            print(f"🟢 Compra {symbol}")

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(10)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    # BOT en segundo plano
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # API
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)