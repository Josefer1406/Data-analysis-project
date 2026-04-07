from flask import Flask, jsonify
import threading
import time
import random

import config
from portfolio import Portfolio

app = Flask(__name__)

# ============================
# 🚀 INICIALIZAR PORTAFOLIO
# ============================
portfolio = Portfolio()

# ============================
# 📊 DATOS SIMULADOS (PUEDES CAMBIAR LUEGO)
# ============================
def obtener_datos():

    oportunidades = []

    for symbol in config.CRYPTOS:
        score = random.randint(0, 3)
        prob = round(random.uniform(0.3, 0.9), 2)
        precio = random.uniform(10, 70000)

        oportunidades.append((symbol, score, prob, precio))

    return oportunidades


# ============================
# 🤖 LOOP DEL BOT
# ============================
def run_bot():

    print("🚀 BOT CUANT INSTITUCIONAL PRO")
    print(f"💰 Capital inicial: {portfolio.capital}")

    while True:

        print("\n🔎 Analizando mercado...")

        oportunidades = obtener_datos()

        # 🧠 CONSTRUIR PORTAFOLIO
        portafolio_objetivo = portfolio.construir_portafolio(oportunidades)

        print("🏆 PORTAFOLIO OBJETIVO:")
        print(portafolio_objetivo)

        # 🟢 COMPRAS
        portfolio.ejecutar_compras(portafolio_objetivo)

        # 📊 PRECIOS ACTUALES (simulados)
        precios_actuales = {s: random.uniform(10, 70000) for s in config.CRYPTOS}

        # 🔴 VENTAS
        portfolio.evaluar_salidas(precios_actuales)

        # 📊 RESUMEN
        portfolio.resumen()

        print("⏳ Ciclo completado...\n")

        time.sleep(config.CYCLE_TIME)


# ============================
# 🌐 API PARA STREAMLIT
# ============================
@app.route("/data")
def data():
    return jsonify({
        "capital": portfolio.capital,
        "posiciones": portfolio.posiciones
    })


# ============================
# 🔄 RESET MANUAL
# ============================
@app.route("/reset")
def reset():
    global portfolio
    portfolio = Portfolio()
    print("🧹 Portfolio reiniciado")
    return "OK"


# ============================
# ▶️ RUN
# ============================
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)