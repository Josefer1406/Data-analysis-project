from flask import Flask, jsonify
import threading, time, datetime, os
import pandas as pd

import config, portfolio

from services.scanner import analizar
from filters.market_filter import mercado_favorable
from core.portfolio_manager import asignar_capital
from core.volatility import ajustar_por_volatilidad
from core.risk_engine import RiskEngine
from core.correlation_filter import filtrar_correlacion

from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)
risk = RiskEngine()

@app.route("/")
def home():
    return "🚀 SISTEMA CUANT INSTITUCIONAL"

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

    portfolio.cargar_estado()
    crear_tablas()

    peak = portfolio.capital

    while True:
        try:

            if not mercado_favorable():
                print("🚫 Mercado no favorable")
                time.sleep(config.CYCLE_TIME)
                continue

            candidatos = []
            prices_dict = {}

            for symbol in config.CRYPTOS:
                score, precio, decision, prob, vol = analizar(symbol)

                prices_dict[symbol] = precio

                if decision == "BUY":
                    candidatos.append((symbol, score, prob, precio, vol))

            if not candidatos:
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # CORRELACIÓN
            # =========================
            df_prices = pd.DataFrame({k: [v] for k, v in prices_dict.items()})
            seleccion = filtrar_correlacion(df_prices)

            candidatos = [c for c in candidatos if c[0] in seleccion]

            # =========================
            # ALLOCATION
            # =========================
            alloc = asignar_capital(
                [(c[0], c[1], c[2], c[3]) for c in candidatos],
                portfolio.capital,
                config.MAX_POSICIONES
            )

            # =========================
            # RISK CONTROL
            # =========================
            if not risk.controlar_drawdown(portfolio.capital, peak):
                print("🛑 STOP TRADING")
                time.sleep(60)
                continue

            peak = max(peak, portfolio.capital)

            # =========================
            # EJECUCIÓN
            # =========================
            for symbol, data_alloc in alloc.items():

                precio = data_alloc["precio"]
                capital = data_alloc["capital"]

                vol = next(c[4] for c in candidatos if c[0] == symbol)

                size = ajustar_por_volatilidad(precio, vol, capital)

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

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))