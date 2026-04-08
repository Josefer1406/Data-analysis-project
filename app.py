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

# ✅ PRECIOS INICIALES REALISTAS
precios = {
    "BTC/USDT": 65000,
    "ETH/USDT": 3500,
    "SOL/USDT": 150,
    "ADA/USDT": 0.5,
    "XRP/USDT": 0.6,
    "AVAX/USDT": 40,
    "LINK/USDT": 20,
    "ATOM/USDT": 12,
}

# ✅ SIMULACIÓN DE MERCADO (movimiento realista)
def actualizar_precio(symbol):
    cambio = random.uniform(-0.005, 0.005)  # ±0.5%
    precios[symbol] *= (1 + cambio)
    return precios[symbol]

def generar_probabilidad():
    return random.uniform(0, 1)

def run_bot():
    while True:
        print("\n🔎 Analizando mercado...")

        for symbol in SYMBOLS:
            prob = generar_probabilidad()
            precio = actualizar_precio(symbol)

            print(f"{symbol} | prob: {prob:.2f} | precio: {precio:.2f}")

            if prob >= config.PROB_MINIMA:
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