from flask import Flask, jsonify
import threading
import time
import datetime
import os

import config
import portfolio

from services.scanner import analizar
from core.risk import calcular_size
from core.portfolio_manager import asignar_capital
from core.correlation_filter import filtrar_correlacion

from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 QUANT FUND ENGINE"

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

def run_bot():

    print("🚀 ENGINE NIVEL FONDO CUANT")

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            print("\n🔎 Analizando mercado...")

            candidatos = []
            precios_dict = {}

            for symbol in config.CRYPTOS:
                try:
                    score, precio, decision, prob = analizar(symbol)

                    precio = float(precio)
                    prob = float(prob)

                    print(f"{symbol} | score: {score} | prob: {round(prob,2)}")

                    precios_dict[symbol] = [precio]

                    if score >= 1:
                        candidatos.append((symbol, score, prob, precio))

                except Exception as e:
                    print(f"❌ Error {symbol}: {e}")

            if not candidatos:
                print("⚠️ Sin oportunidades")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # FILTRO DE CORRELACIÓN
            # =========================
            seleccion = filtrar_correlacion(precios_dict)

            candidatos = [c for c in candidatos if c[0] in seleccion]

            # =========================
            # ALLOCATION
            # =========================
            allocation = asignar_capital(
                candidatos,
                portfolio.capital,
                config.MAX_POSICIONES
            )

            print("\n🏆 PORTFOLIO ALLOCATION:")
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

                    print(f"🔴 SELL {symbol}")

            # =========================
            # APERTURAS
            # =========================
            for symbol, data_alloc in allocation.items():

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

                    print(f"🟢 BUY {symbol} (allocation)")

            print(f"\n💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print("⏳ Ciclo completado...\n")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)