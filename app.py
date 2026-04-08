import time
from flask import Flask, jsonify
from threading import Thread

import config
from services.scanner import analizar
from portfolio import Portfolio

app = Flask(__name__)

# =========================
# INSTANCIA GLOBAL
# =========================
portfolio = Portfolio()


# =========================
# BOT LOOP (HEDGE BASE)
# =========================
def bot():

    print("🚀 BOT INSTITUCIONAL INICIADO")

    while True:
        try:
            print("\n🔎 Analizando mercado...")

            ranking = []

            # =========================
            # 1. ESCANEO DE MERCADO
            # =========================
            for symbol in config.CRYPTOS:
                try:
                    data = analizar(symbol)

                    if data is None:
                        continue

                    ranking.append(data)

                except Exception as e:
                    print(f"Error analizando {symbol}: {e}")

            if not ranking:
                print("⚠️ Sin datos de mercado")
                time.sleep(10)
                continue

            # =========================
            # 2. ORDENAR POR PROBABILIDAD
            # =========================
            ranking = sorted(ranking, key=lambda x: x["prob"], reverse=True)

            # =========================
            # 3. EVALUAR SALIDAS
            # =========================
            for symbol in list(portfolio.posiciones.keys()):
                try:
                    data = analizar(symbol)

                    if data is None:
                        continue

                    precio = data["precio"]

                    if portfolio.evaluar(symbol, precio):
                        portfolio.cerrar(symbol, precio)

                except Exception as e:
                    print(f"Error salida {symbol}: {e}")

            # =========================
            # 4. ENTRADAS (TOP OPORTUNIDADES)
            # =========================
            for data in ranking:

                symbol = data["symbol"]
                precio = data["precio"]
                prob = data["prob"]
                vol = data["vol"]

                try:
                    if portfolio.comprar(symbol, precio, prob, vol):
                        print(f"🟢 Compra ejecutada: {symbol}")

                except Exception as e:
                    print(f"Error compra {symbol}: {e}")

            # =========================
            # 5. ESTADO
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")

            time.sleep(10)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(5)


# =========================
# API PARA STREAMLIT
# =========================
@app.route("/data")
def data():
    return jsonify(portfolio.data())


# =========================
# START
# =========================
if __name__ == "__main__":

    hilo = Thread(target=bot)
    hilo.daemon = True
    hilo.start()

    print("🚀 BOT INICIADO (única instancia)")

    app.run(host="0.0.0.0", port=8080)