from flask import Flask, jsonify
import threading
import time
import config
import json
import os

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)

# =========================
# IA STORAGE
# =========================
IA_FILE = "ia_state.json"

def cargar_ia():
    if os.path.exists(IA_FILE):
        with open(IA_FILE, "r") as f:
            return json.load(f)
    return {"wins": 0, "losses": 0, "prob_min": 0.75}

def guardar_ia(data):
    with open(IA_FILE, "w") as f:
        json.dump(data, f)

ia = cargar_ia()


# =========================
# SCORE INTELIGENTE
# =========================
def score(asset):
    return (asset["prob"] * 0.7) + ((asset["score"] / 3) * 0.3)


# =========================
# FILTRO IA
# =========================
def es_valido(asset):

    prob_min = ia["prob_min"]

    if asset["prob"] < prob_min:
        return False

    if asset["score"] < 1:
        return False

    return True


# =========================
# AJUSTE IA DINÁMICO
# =========================
def ajustar_ia():

    total = ia["wins"] + ia["losses"]

    if total < 20:
        return

    winrate = ia["wins"] / total

    # 🔥 si pierde mucho → más estricto
    if winrate < 0.4:
        ia["prob_min"] = min(0.85, ia["prob_min"] + 0.01)

    # 🔥 si gana → más agresivo
    elif winrate > 0.6:
        ia["prob_min"] = max(0.65, ia["prob_min"] - 0.01)

    guardar_ia(ia)


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT HEDGE FUND IA ACTIVADO")

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
            # 🔥 CIERRE INTELIGENTE
            # =========================
            for symbol, pos in list(portfolio.posiciones.items()):

                precio_actual = precios.get(symbol, pos["entry"])
                pnl = (precio_actual - pos["entry"]) / pos["entry"]

                # take profit
                if pnl > 0.012:
                    print(f"🟢 TP {symbol} {round(pnl,4)}")
                    portfolio.cerrar(symbol, precio_actual, pnl)
                    ia["wins"] += 1

                # stop loss
                elif pnl < -0.01:
                    print(f"🔴 SL {symbol} {round(pnl,4)}")
                    portfolio.cerrar(symbol, precio_actual, pnl)
                    ia["losses"] += 1

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

                if mejor["prob"] > peor_prob + 0.08:
                    print(f"🔄 ROTANDO {peor_symbol} → {mejor['symbol']}")
                    portfolio.cerrar(peor_symbol, precios.get(peor_symbol, 0), 0)

                    portfolio.comprar(
                        mejor["symbol"],
                        mejor["precio"],
                        mejor["prob"]
                    )

            # =========================
            # LLENAR POSICIONES
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios > 0:

                print(f"📈 Llenando {espacios} posiciones")

                for asset in candidatos:

                    if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                        break

                    portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

            # =========================
            # IA UPDATE
            # =========================
            ajustar_ia()

            # =========================
            # LOGS
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📈 Candidatos: {len(candidatos)}")
            print(f"🧠 IA Win/Loss: {ia['wins']}/{ia['losses']}")
            print(f"🎯 Prob mínima: {round(ia['prob_min'],2)}")

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