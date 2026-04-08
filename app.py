from flask import Flask, jsonify
import time
import random
from portfolio import Portfolio
import config

app = Flask(__name__)
portfolio = Portfolio()

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT",
    "ADA/USDT", "XRP/USDT", "AVAX/USDT",
    "LINK/USDT", "ATOM/USDT"
]

# ✅ PROBABILIDAD SIMULADA
def generar_probabilidad():
    return random.uniform(0, 1)

# ✅ PRECIOS REALISTAS
def generar_precio(symbol):
    precios = {
        "BTC/USDT": random.uniform(60000, 70000),
        "ETH/USDT": random.uniform(3000, 4000),
        "SOL/USDT": random.uniform(100, 200),
        "ADA/USDT": random.uniform(0.3, 0.8),
        "XRP/USDT": random.uniform(0.4, 0.9),
        "AVAX/USDT": random.uniform(20, 60),
        "LINK/USDT": random.uniform(10, 30),
        "ATOM/USDT": random.uniform(8, 20),
    }
    return precios.get(symbol, 100)

def run_bot():
    while True:
        print("\n🔎 Analizando mercado...")

        for symbol in SYMBOLS:
            prob = generar_probabilidad()

            print(f"{symbol} | prob: {prob:.2f}")

            if prob < config.PROB_MINIMA:
                continue

            precio = generar_precio(symbol)

            portfolio.comprar(symbol, precio, prob)

            if symbol in portfolio.posiciones:
                portfolio.vender(symbol, precio)

        estado = portfolio.estado()

        print(f"💰 Capital: {estado['capital']:.2f}")
        print(f"📊 Posiciones: {estado['posiciones']}")
        print("⏳ Ciclo completado...")

        time.sleep(10)


@app.route("/data")
def data():
    return jsonify(portfolio.estado())


if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)