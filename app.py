from flask import Flask, jsonify
from portfolio import Portfolio
import threading
import time
import random

app = Flask(__name__)
portfolio = Portfolio()

def bot():

    print("🚀 BOT INICIADO (única instancia)")

    while True:

        precios = {
            "BTC/USDT": 60000 + random.uniform(-300, 300),
            "ETH/USDT": 3400 + random.uniform(-50, 50),
            "SOL/USDT": 150 + random.uniform(-5, 5),
            "ADA/USDT": 0.5 + random.uniform(-0.02, 0.02),
            "XRP/USDT": 0.6 + random.uniform(-0.02, 0.02),
            "AVAX/USDT": 35 + random.uniform(-2, 2),
            "LINK/USDT": 18 + random.uniform(-1, 1),
            "ATOM/USDT": 10 + random.uniform(-1, 1)
        }

        for s, p in precios.items():
            prob = random.random()
            portfolio.comprar(s, p, prob)

        portfolio.evaluar(precios)

        print(f"💰 Capital: {portfolio.capital:.2f}")
        print(f"📊 Posiciones: {portfolio.posiciones}")

        time.sleep(10)

@app.route("/data")
def data():
    return jsonify(portfolio.data())

if __name__ == "__main__":
    threading.Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)