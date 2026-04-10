from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# SCORE REAL
# =========================
def score(asset):
    return (asset["prob"] * 0.7) + ((asset["score"] / 3) * 0.3)


# =========================
# FILTRO FLEXIBLE
# =========================
def es_valido(asset):

    # 🔥 MÁS PERMISIVO (clave)
    if asset["prob"] < 0.70:
        return False

    if asset["score"] < 1:
        return False

    return True


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT RENTABLE ACTIVADO")

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
            # ORDENAR
            # =========================
            candidatos = sorted(
                candidatos,
                key=lambda x: x["score_final"],
                reverse=True
            )

            # =========================
            # 🔥 ROTACIÓN REAL
            # =========================
            if portfolio.posiciones and candidatos:

                mejor = candidatos[0]

                peor_symbol = None
                peor_score = 999

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_score:
                        peor_score = pos["prob"]
                        peor_symbol = s

                # 🔥 MÁS AGRESIVO
                if mejor["prob"] > peor_score + 0.05:
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
            # 🔥 LLENAR POSICIONES SIEMPRE
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios > 0:

                print(f"📈 Buscando llenar {espacios} posiciones")

                for asset in candidatos:

                    if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                        break

                    portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

            # =========================
            # COOLDOWN
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # LOGS
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📈 Candidatos: {len(candidatos)}")

            time.sleep(config.CYCLE_TIME)

        except Exception as e:
            print(f"❌ ERROR BOT: {e}")
            time.sleep(5)


@app.route("/data")
def data():
    return jsonify(portfolio.data())


if __name__ == "__main__":
    threading.Thread(target=bot).start()
    app.run(host="0.0.0.0", port=8080)