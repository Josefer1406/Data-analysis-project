from flask import Flask, jsonify
import threading, time, datetime, os

import config, portfolio, adaptive
from services.scanner import analizar
from core.risk import calcular_size

from database import crear_tablas, insertar_trade, obtener_trades
from ml.train import entrenar

app = Flask(__name__)

@app.route("/")
def home():
    return "SYSTEM LIVE"

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
    portfolio.cargar_estado()
    crear_tablas()
    ciclo = 0

    while True:
        try:
            ciclo += 1
            params = adaptive.ajustar_parametros()

            ranking = []

            for s in config.CRYPTOS:
                sc, p, d = analizar(s)
                ranking.append((s, sc, p, d))

            ranking.sort(key=lambda x: x[1], reverse=True)

            # CIERRES
            for s in list(portfolio.posiciones.keys()):
                precio = next((p for sym, sc, p, d in ranking if sym == s), None)
                if precio and portfolio.evaluar_salida(s, precio):
                    size = portfolio.posiciones[s]["size"]
                    pnl = portfolio.cerrar_posicion(s, precio)

                    insertar_trade(datetime.datetime.now(), s, "SELL", precio, size, pnl, portfolio.capital)

            # APERTURAS
            for s, sc, p, d in ranking[:config.MAX_POSICIONES]:
                if d == "BUY":
                    size = calcular_size(p)
                    if portfolio.abrir_posicion(s, p, size):
                        insertar_trade(datetime.datetime.now(), s, "BUY", p, size, 0, portfolio.capital)

            if ciclo % 10 == 0:
                entrenar()

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))