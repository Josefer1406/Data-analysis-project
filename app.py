from flask import Flask, jsonify
import threading
import time
import config
from services.scanner import analizar
from portfolio import Portfolio

app = Flask(__name__)

bot = Portfolio()

def run_bot():

    print("🚀 BOT INSTITUCIONAL INICIADO")

    while True:
        try:
            signals = []
            precios = {}

            for symbol in config.CRYPTOS:
                data = analizar(symbol)
                if data:
                    signals.append(data)
                    precios[symbol] = data["precio"]

            signals = sorted(signals, key=lambda x: x["prob"], reverse=True)

            bot.actualizar(precios)

            for s in signals:
                bot.abrir(s)

            print(f"💰 Capital: {bot.capital}")
            print(f"📊 Posiciones: {list(bot.posiciones.keys())}")

            time.sleep(config.COOLDOWN_BASE)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(10)

@app.route("/data")
def data():
    return jsonify(bot.data())

# 🔥 HILO DEL BOT
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)