from flask import Flask, jsonify
import threading
import time
import datetime
import os

import config
import portfolio

from services.scanner import analizar
from core.portfolio_optimizer import optimizar_portafolio
from database import crear_tablas, insertar_trade, obtener_trades, reset_database

app = Flask(__name__)

# =========================
# API
# =========================
@app.route("/")
def home():
    return "🚀 QUANT FUND ENGINE FINAL ESTABLE"

@app.route("/data")
def data():
    rows = obtener_trades()

    return jsonify([
        {
            "fecha": r[1],
            "symbol": r[2],
            "tipo": r[3],
            "precio": float(r[4]),
            "size": float(r[5]),
            "pnl": float(r[6]),
            "capital": float(r[7])
        } for r in rows
    ])

# =========================
# 🔥 RESET TOTAL
# =========================
@app.route("/reset")
def reset():
    reset_database()
    portfolio.reset_portfolio()
    return "🧹 RESET TOTAL: DB + CAPITAL + POSICIONES"

# =========================
# BOT ENGINE
# =========================
def run_bot():

    print("🚀 SISTEMA CUANT INSTITUCIONAL ESTABLE")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            print("\n🔎 Analizando mercado...")

            candidatos = []

            # =========================
            # SCANNER
            # =========================
            for symbol in config.CRYPTOS:
                try:
                    score, precio, decision, prob = analizar(symbol)

                    precio = float(precio)
                    prob = float(prob)

                    print(f"{symbol} | score: {score} | prob: {round(prob,2)}")

                    if score >= 1:
                        candidatos.append((symbol, score, prob, precio))

                except Exception as e:
                    print(f"❌ Error {symbol}: {e}")

            if not candidatos:
                print("⚠️ Sin oportunidades")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # OPTIMIZACIÓN PORTAFOLIO
            # =========================
            allocation = optimizar_portafolio(
                candidatos,
                portfolio.capital,
                config.MAX_POSICIONES
            )

            print("\n🏆 PORTAFOLIO ÓPTIMO:")
            print(allocation)

            # =========================
            # CIERRES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):

                precio_actual = next(
                    (c[3] for c in candidatos if c[0] == symbol),
                    None
                )

                if precio_actual and portfolio.evaluar_salida(symbol, precio_actual):

                    size = portfolio.posiciones[symbol]["size"]
                    pnl = portfolio.cerrar_posicion(symbol, precio_actual)

                    insertar_trade(
                        datetime.datetime.now(),
                        symbol,
                        "SELL",
                        float(precio_actual),
                        float(size),
                        float(pnl),
                        float(portfolio.capital)
                    )

                    print(f"🔴 SELL {symbol} | PnL: {round(pnl,2)}")

            # =========================
            # APERTURAS CONTROLADAS
            # =========================
            for symbol, data_alloc in allocation.items():

                # 🔥 evitar sobrecompra
                if symbol in portfolio.posiciones:
                    continue

                precio = data_alloc["precio"]
                capital_asignado = data_alloc["capital"]

                size = capital_asignado / precio

                if portfolio.abrir_posicion(symbol, precio, size):

                    insertar_trade(
                        datetime.datetime.now(),
                        symbol,
                        "BUY",
                        float(precio),
                        float(size),
                        0.0,
                        float(portfolio.capital)
                    )

                    print(f"🟢 BUY {symbol} | peso: {round(data_alloc['peso'],2)}")

            # =========================
            # ESTADO
            # =========================
            print(f"\n💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print("⏳ Ciclo completado...\n")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {e}")
            time.sleep(10)

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)