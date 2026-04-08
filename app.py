import time
import threading
from flask import Flask, jsonify

import config
import portfolio
from ml import model

# =========================
# CONFIG
# =========================

UNIVERSO = [
    "BTC/USDT","ETH/USDT","SOL/USDT",
    "ADA/USDT","XRP/USDT","AVAX/USDT",
    "LINK/USDT","ATOM/USDT"
]

# =========================
# ESTADO GLOBAL
# =========================

historial_operaciones = []

# =========================
# BOT PRINCIPAL
# =========================

def run_bot():
    print("🚀 BOT CUANT INSTITUCIONAL PRO (ESTABLE)")

    while True:
        print("\n🔎 Analizando mercado...")

        señales = []

        for symbol in UNIVERSO:
            data = model.analizar_activo(symbol)

            print(f"{symbol} | score: {data['score']} | prob: {data['probabilidad']}")

            if data["score"] >= config.MIN_SCORE:
                señales.append(data)

        señales.sort(key=lambda x: x["probabilidad"], reverse=True)

        entradas = 0

        for s in señales:
            if entradas >= config.MAX_ENTRADAS_POR_CICLO:
                break

            if portfolio.puede_comprar(s["symbol"]):

                capital_antes = portfolio.capital

                portfolio.abrir_posicion(
                    s["symbol"],
                    s["probabilidad"],
                    s["precio"]
                )

                capital_despues = portfolio.capital

                # Registrar solo si realmente compró
                if capital_despues < capital_antes:
                    historial_operaciones.append({
                        "symbol": s["symbol"],
                        "tipo": "BUY",
                        "capital": float(capital_despues),
                        "probabilidad": float(s["probabilidad"])
                    })

                    entradas += 1

        # =========================
        # GESTIÓN DE RIESGO
        # =========================

        posiciones_antes = list(portfolio.posiciones.keys())

        portfolio.gestionar_riesgo()

        posiciones_despues = list(portfolio.posiciones.keys())

        cerradas = set(posiciones_antes) - set(posiciones_despues)

        for symbol in cerradas:
            historial_operaciones.append({
                "symbol": symbol,
                "tipo": "SELL",
                "capital": float(portfolio.capital),
                "probabilidad": None
            })

        portfolio.actualizar_cooldowns()
        portfolio.estado()

        print("⏳ Ciclo completado...\n")
        time.sleep(10)

# =========================
# FLASK API
# =========================

app = Flask(__name__)

@app.route("/data")
def data():
    try:
        posiciones_limpias = {
            str(k): {
                "inversion": float(v.get("inversion", 0)),
                "entry": float(v.get("entry", 0))
            }
            for k, v in portfolio.posiciones.items()
        }

        historial_limpio = []
        for h in historial_operaciones:
            historial_limpio.append({
                "symbol": str(h.get("symbol", "")),
                "tipo": str(h.get("tipo", "")),
                "capital": float(h.get("capital", 0)),
                "probabilidad": float(h["probabilidad"]) if h.get("probabilidad") is not None else None
            })

        return jsonify({
            "capital": float(portfolio.capital),
            "posiciones": posiciones_limpias,
            "historial": historial_limpio
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# START
# =========================

def start_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    start_flask()