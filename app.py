from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# SCORING INSTITUCIONAL
# =========================
def score_institucional(asset):

    prob = asset["prob"]
    score = asset["score"]

    # base combinado
    s = (prob * 0.6) + ((score / 3) * 0.4)

    # bonus convicción alta
    if prob > 0.9:
        s += 0.1

    return s


# =========================
# FILTRO ULTRA SELECTIVO
# =========================
def filtro_calidad(asset):

    if asset["prob"] < 0.82:
        return False

    if asset["score"] < 2:
        return False

    if asset["precio"] <= 0:
        return False

    return True


# =========================
# BOT PRINCIPAL
# =========================
def bot():

    print("🚀 BOT HEDGE FUND REAL INICIADO")

    contador = 0

    while True:
        try:
            contador += 1

            print("\n🔎 Analizando mercado...")

            candidatos = []
            precios = {}

            # =========================
            # SCAN
            # =========================
            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None:
                    continue

                precios[symbol] = data["precio"]

                if not filtro_calidad(data):
                    continue

                data["score_final"] = score_institucional(data)

                candidatos.append(data)

            # =========================
            # GESTIÓN POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # SIN EDGE = NO TRADE
            # =========================
            if not candidatos:
                print("⛔ NO TRADE (mercado sin ventaja)")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # RANKING REAL
            # =========================
            candidatos = sorted(
                candidatos,
                key=lambda x: x["score_final"],
                reverse=True
            )

            # =========================
            # CONTROL DE CAPACIDAD
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios <= 0:
                print("📊 Portafolio lleno (esperando salida)")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # SELECCIÓN FINAL (TOP REAL)
            # =========================
            seleccion = candidatos[:espacios]

            # =========================
            # EJECUCIÓN
            # =========================
            for asset in seleccion:

                ejecutado = portfolio.comprar(
                    asset["symbol"],
                    asset["precio"],
                    asset["prob"]
                )

                if ejecutado:
                    print(
                        f"🟢 TRADE: {asset['symbol']} | "
                        f"prob {round(asset['prob'],2)} | "
                        f"score {round(asset['score_final'],2)}"
                    )

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # GUARDADO RESULTADOS
            # =========================
            if contador % 20 == 0:
                try:
                    portfolio.guardar_resultados()
                    print("💾 Resultados guardados")
                except Exception as e:
                    print(f"⚠️ Error guardando: {e}")

            # =========================
            # LOGS
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📈 Candidatos: {len(candidatos)}")
            print(f"⏱ Cooldown: {portfolio.cooldown}s")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(5)


# =========================
# API STREAMLIT
# =========================
@app.route("/data")
def data():
    return jsonify(portfolio.data())


# =========================
# RUN
# =========================
if __name__ == "__main__":
    threading.Thread(target=bot).start()
    app.run(host="0.0.0.0", port=8080)