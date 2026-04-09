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

    s = (prob * 0.6) + ((score / 3) * 0.4)

    if prob > 0.9:
        s += 0.1

    return s


# =========================
# FILTRO DINÁMICO PRO
# =========================
def clasificar_trade(asset):

    prob = asset["prob"]
    score = asset["score"]

    # 🔥 ELITE
    if prob >= 0.80 and score >= 2:
        return "elite"

    # 🔥 OPORTUNISTA (mercado lento)
    if prob >= 0.70 and score >= 1:
        return "oportunista"

    return None


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT HEDGE FUND ADAPTATIVO INICIADO")

    contador = 0

    while True:
        try:
            contador += 1

            print("\n🔎 Analizando mercado...")

            elite = []
            oportunistas = []
            precios = {}

            # =========================
            # SCAN
            # =========================
            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None:
                    continue

                precios[symbol] = data["precio"]

                tipo = clasificar_trade(data)

                if tipo is None:
                    continue

                data["score_final"] = score_institucional(data)

                if tipo == "elite":
                    elite.append(data)
                else:
                    oportunistas.append(data)

            # =========================
            # ACTUALIZAR PORTAFOLIO
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # ORDENAR
            # =========================
            elite = sorted(elite, key=lambda x: x["score_final"], reverse=True)
            oportunistas = sorted(oportunistas, key=lambda x: x["score_final"], reverse=True)

            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios <= 0:
                print("📊 Portafolio lleno")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # PRIORIDAD: ELITE
            # =========================
            seleccion = elite[:espacios]

            # =========================
            # SI NO HAY ELITE → USAR OPORTUNISTAS
            # =========================
            if not seleccion:
                print("⚠️ Usando trades oportunistas")
                seleccion = oportunistas[:espacios]

            if not seleccion:
                print("⛔ NO TRADE (ni elite ni oportunistas)")
                time.sleep(config.CYCLE_TIME)
                continue

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
                        f"{'ELITE' if asset in elite else 'OPORTUNISTA'} | "
                        f"prob {round(asset['prob'],2)}"
                    )

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # GUARDADO
            # =========================
            if contador % 20 == 0:
                portfolio.guardar_resultados()

            # =========================
            # LOGS
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"🔥 Elite: {len(elite)} | Oportunistas: {len(oportunistas)}")
            print(f"⏱ Cooldown: {portfolio.cooldown}s")

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