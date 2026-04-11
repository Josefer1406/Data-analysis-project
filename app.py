from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# SCORE INSTITUCIONAL
# =========================
def score(asset):
    return (asset["prob"] * 0.6) + ((asset["score"] / 5) * 0.4)


# =========================
# FILTRO BALANCEADO
# =========================
def es_valido(asset):

    # 🔥 MÁS FLEXIBLE PERO CONTROLADO
    if asset["prob"] < 0.55:
        return False

    if asset["score"] < 2:
        return False

    return True


# =========================
# BOT PRINCIPAL
# =========================
def bot():

    print("🚀 BOT BALANCEADO ACTIVADO")

    while True:
        try:

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

                if es_valido(data):
                    data["score_final"] = score(data)
                    candidatos.append(data)

            # =========================
            # ACTUALIZAR POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # SIN CANDIDATOS
            # =========================
            if not candidatos:
                print("⛔ Sin candidatos válidos")
                print(f"💰 Capital: {round(portfolio.capital,2)}")
                print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # ORDENAR
            # =========================
            candidatos = sorted(
                candidatos,
                key=lambda x: x["score_final"],
                reverse=True
            )

            # =========================
            # 🔥 ROTACIÓN INTELIGENTE
            # =========================
            if portfolio.posiciones:

                mejor = candidatos[0]

                peor_symbol = None
                peor_score = 999

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_score:
                        peor_score = pos["prob"]
                        peor_symbol = s

                # 🔥 MÁS FRECUENTE
                if mejor["prob"] > peor_score + 0.03:
                    print(f"🔄 ROTANDO {peor_symbol} → {mejor['symbol']}")

                    portfolio.cerrar(
                        peor_symbol,
                        precios.get(peor_symbol, 0),
                        0
                    )

                    portfolio.comprar(
                        mejor["symbol"],
                        mejor["precio"],
                        mejor["prob"]
                    )

            # =========================
            # 🔥 LLENADO INTELIGENTE
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios > 0:

                print(f"📈 Llenando hasta {config.MAX_POSICIONES} posiciones")

                for asset in candidatos:

                    if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                        break

                    ejecutado = portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

                    if ejecutado:
                        print(f"🟢 BUY {asset['symbol']} | prob {asset['prob']}")

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # LOGS CLAROS
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
# API
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