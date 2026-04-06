from flask import Flask, jsonify
import threading, time, datetime, os
import numpy as np

import config, portfolio
from services.scanner import analizar
from core.portfolio_manager import asignar_capital
from core.risk_engine import RiskEngine
from database import crear_tablas, insertar_trade, obtener_trades

app = Flask(__name__)

risk = RiskEngine()
peak_capital = 1000

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

def bot():

    global peak_capital

    portfolio.cargar_estado()
    crear_tablas()

    while True:
        try:

            signals = []

            for s in config.CRYPTOS:
                symbol, score, X, precio = analizar(s)

                prob = np.random.uniform(0.4, 0.7)  # placeholder ML
                signals.append((symbol, score, prob, precio))

            # =========================
            # PORTFOLIO ALLOCATION
            # =========================
            alloc = asignar_capital(
                [(s, sc, pr) for s, sc, pr, p in signals],
                portfolio.capital
            )

            # =========================
            # RISK CONTROL
            # =========================
            if not risk.check_drawdown(portfolio.capital, peak_capital):
                print("STOP TRADING - drawdown")
                time.sleep(60)
                continue

            peak_capital = max(peak_capital, portfolio.capital)

            # =========================
            # EXECUTION
            # =========================
            for symbol, score, prob, precio in signals:

                if symbol in alloc:

                    capital_asignado = alloc[symbol]
                    size = capital_asignado / precio

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

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))