import time
import threading
from flask import Flask, jsonify

import config
import portfolio
from ml import model

# =========================
# CONFIG BOT
# =========================

UNIVERSO = [
    "BTC/USDT","ETH/USDT","SOL/USDT",
    "ADA/USDT","XRP/USDT","AVAX/USDT",
    "LINK/USDT","ATOM/USDT"
]

# =========================
# ESTADO GLOBAL (para dashboard)
# =========================

historial_operaciones = []

# =========================
# BOT PRINCIPAL
# =========================

def run_bot():
    print("🚀 BOT CUANT INSTITUCIONAL PRO (POSITION SIZING)")

    while True:
        print("\n🔎 Analizando mercado...")

        señales = []

        for symbol in UNIVERSO:
            data = model.analizar_activo(symbol)

            print(f"{symbol} | score: {data['score']} | prob: {data['probabilidad']}")

            if data["score"] >= config.MIN_SCORE:
                señales.append(data)

        # ordenar por mejor oportunidad
        señales.sort(key=lambda x: x["probabilidad"], reverse=True)

        entradas = 0

        for s in señales:
            if entradas >= config.MAX_ENTRADAS_POR_CICLO:
                break

            if portfolio.puede_comprar(s["symbol"]):
                antes = portfolio.capital

                portfolio.abrir_posicion(
                    s["symbol"],
                    s["probabilidad"],
                    s["precio"]
                )

                despues = portfolio.capital

                # registrar operación si hubo cambio real
                if despues < antes:
                    historial_operaciones.append({
                        "symbol": s["symbol"],
                        "tipo": "BUY",
                        "capital": despues,
                        "probabilidad": s["probabilidad"]
                    })

                    entradas += 1

        # =========================
        # GESTIÓN DE RIESGO
        # =========================

        posiciones_antes = list(portfolio.posiciones.keys())

        portfolio.gestionar_riesgo()

        posiciones_despues = list(portfolio.posiciones.keys())

        # detectar cierres
        cerradas = set(posiciones_antes) - set(posiciones_despues)

        for symbol in cerradas:
            historial_operaciones.append({
                "symbol": symbol,
                "tipo": "SELL",
                "capital": portfolio.capital
            })

        portfolio.actualizar_cooldowns()
        portfolio.estado()

        print("⏳ Ciclo completado...\n")
        time.sleep(10)

# =========================
# FLASK API (STREAMLIT)
# =========================

app = Flask(__name__)

@app.route("/data")
def data():
    return jsonify({
        "capital": round(portfolio.capital, 2),
        "posiciones": portfolio.posiciones,
        "historial": historial_operaciones
    })

# =========================
# START SERVICIOS
# =========================

def start_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # iniciar bot en paralelo
    threading.Thread(target=run_bot, daemon=True).start()

    # iniciar API
    start_flask()