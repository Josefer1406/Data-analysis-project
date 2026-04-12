from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# CONFIG PRO
# =========================
MAX_POSICIONES = 4
RESERVA = 0.40
INV_ELITE = 0.15
INV_NORMAL = 0.10


# =========================
# SCORE
# =========================
def score(asset):
    return (asset["prob"] * 0.65) + ((asset["score"] / 5) * 0.35)


# =========================
# CLASIFICACIÓN
# =========================
def clasificar(asset):

    if asset["prob"] >= 0.75 and asset["score"] >= 3:
        return "elite"

    if asset["prob"] >= 0.60 and asset["score"] >= 2:
        return "buena"

    return None


# =========================
# ANTI CORRELACIÓN
# =========================
def correlacionado(symbol, posiciones):

    base = symbol.split("/")[0]

    for p in posiciones:
        if base in p:
            return True

    return False


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT PRO RENTABLE ACTIVADO")

    while True:
        try:

            print("\n🔎 Analizando mercado...")

            candidatos = []
            precios = {}

            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None:
                    continue

                precios[symbol] = data["precio"]

                tipo = clasificar(data)

                if tipo is None:
                    continue

                data["tipo"] = tipo
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
            # ROTACIÓN INTELIGENTE
            # =========================
            if portfolio.posiciones and candidatos:

                mejor = candidatos[0]

                peor_symbol = None
                peor_prob = 999

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_prob:
                        peor_prob = pos["prob"]
                        peor_symbol = s

                if mejor["prob"] > peor_prob + 0.05:
                    print(f"🔄 ROTANDO {peor_symbol} → {mejor['symbol']}")

                    portfolio.cerrar(
                        peor_symbol,
                        precios.get(peor_symbol, 0),
                        0
                    )

            # =========================
            # CAPITAL DISPONIBLE
            # =========================
            capital_total = portfolio.capital
            capital_operable = capital_total * (1 - RESERVA)

            # =========================
            # LLENAR POSICIONES
            # =========================
            for asset in candidatos:

                if len(portfolio.posiciones) >= MAX_POSICIONES:
                    break

                if asset["symbol"] in portfolio.posiciones:
                    continue

                if correlacionado(asset["symbol"], portfolio.posiciones):
                    continue

                if asset["tipo"] == "elite":
                    inversion = capital_operable * INV_ELITE
                else:
                    inversion = capital_operable * INV_NORMAL

                ejecutado = portfolio.comprar(
                    asset["symbol"],
                    asset["precio"],
                    asset["prob"],
                    inversion
                )

                if ejecutado:
                    print(
                        f"🟢 BUY {asset['symbol']} | "
                        f"{asset['tipo']} | "
                        f"${round(inversion,2)}"
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