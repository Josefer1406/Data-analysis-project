from flask import Flask, jsonify
import threading
import time
import datetime
import os
import numpy as np

import config
import portfolio
import adaptive

from services.scanner import analizar
from core.risk import calcular_size

from database import crear_tablas, insertar_trade, obtener_trades
from ml.train import entrenar

# =========================
# FLASK APP
# =========================
app = Flask(__name__)

# =========================
# RUTA HOME (IMPORTANTE)
# =========================
@app.route("/")
def home():
    return "🚀 BOT CUANT ACTIVO - API OK"

# =========================
# API DATA
# =========================
@app.route("/data")
def data():
    try:
        rows = obtener_trades()

        data = []
        for r in rows:
            data.append({
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

    print("🤖 BOT CUANT INSTITUCIONAL INICIADO")

    portfolio.cargar_estado()
    crear_tablas()

    ciclos = 0
    peak_capital = portfolio.capital

    while True:
        try:
            ciclos += 1

            # =========================
            # AUTO-OPTIMIZACIÓN
            # =========================
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

            # =========================
            # ORDENAR
            # =========================
            ranking.sort(key=lambda x: x[1], reverse=True)
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # CIERRE DE POSICIONES
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
            # APERTURA DE POSICIONES
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

            # =========================
            # CONTROL DE DRAWDOWN
            # =========================
            peak_capital = max(peak_capital, portfolio.capital)

            drawdown = (portfolio.capital - peak_capital) / peak_capital

            if drawdown < -0.2:
                print("🛑 STOP: Drawdown máximo alcanzado")
                time.sleep(60)
                continue

            # =========================
            # AUTO-ML
            # =========================
            if ciclos % 10 == 0:
                print("🧠 Reentrenando modelo...")
                try:
                    entrenar()
                except Exception as e:
                    print(f"Error entrenamiento ML: {e}")

            # =========================
            # LOG
            # =========================
            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print("⏳ Esperando próximo ciclo...\n")

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