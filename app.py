from flask import Flask, jsonify
import threading
import time
import datetime
import os

import config
import portfolio

from services.scanner import analizar
from filters.market_filter import mercado_favorable
from core.portfolio_manager import asignar_capital
from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 BOT CUANT PORTFOLIO PRO"

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

    print("🤖 BOT PORTFOLIO PRO INICIADO")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            # =========================
            # FILTRO DE MERCADO
            # =========================
            if not mercado_favorable():
                print("🚫 Mercado no favorable")
                time.sleep(config.CYCLE_TIME)
                continue

            candidatos = []

            for symbol in config.CRYPTOS:
                try:
                    score, precio, decision, prob = analizar(symbol)

                    if decision == "BUY":
                        candidatos.append((symbol, score, prob, precio))

                except Exception as e:
                    print(f"Error {symbol}: {e}")

            if not candidatos:
                print("⚠️ No hay oportunidades")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # ALLOCATION INTELIGENTE
            # =========================
            allocation = asignar_capital(
                candidatos,
                portfolio.capital,
                config.MAX_POSICIONES
            )

            # =========================
            # CIERRES
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                try:
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
                            precio_actual,
                            size,
                            pnl,
                            portfolio.capital
                        )

                        print(f"🔴 SELL {symbol}")

                except Exception as e:
                    print(f"Error cierre {symbol}: {e}")

            # =========================
            # APERTURAS PRO
            # =========================
            for symbol, data_alloc in allocation.items():

                capital_asignado = data_alloc["capital"]
                precio = data_alloc["precio"]

                size = capital_asignado / precio

                try:
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

                        print(f"🟢 BUY {symbol} (capital: {round(capital_asignado,2)})")

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            print(f"💰 Capital total: {portfolio.capital}")
            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))