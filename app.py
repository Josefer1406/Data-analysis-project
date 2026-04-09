from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# SCORING
# =========================
def score_institucional(asset):

    prob = asset["prob"]
    score = asset["score"]

    s = (prob * 0.6) + ((score / 3) * 0.4)

    if prob > 0.9:
        s += 0.1

    return s


# =========================
# CLASIFICACIÓN
# =========================
def clasificar_trade(asset):

    prob = asset["prob"]
    score = asset["score"]

    if prob >= 0.80 and score >= 2:
        return "elite"

    if prob >= 0.70 and score >= 1:
        return "oportunista"

    return None


# =========================
# BOT
# =========================
def bot():

    print("🚀 BOT HEDGE FUND UNIVERSO DINÁMICO")

    contador = 0

    while True:
        try:
            contador += 1

            print("\n🔎 Analizando mercado...")

            ranking_total = []
            precios = {}

            # =========================
            # SCAN GLOBAL
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

                ranking_total.append(data)

            # =========================
            # ACTUALIZAR POSICIONES
            # =========================
            portfolio.actualizar(precios)

            if not ranking_total:
                print("⛔ No hay activos válidos")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # 🔥 UNIVERSO DINÁMICO
            # =========================
            ranking_total = sorted(
                ranking_total,
                key=lambda x: x["score_final"],
                reverse=True
            )

            universo = ranking_total[:8]  # 🔥 SOLO LOS MEJORES

            # =========================
            # DIVIDIR
            # =========================
            elite = [a for a in universo if clasificar_trade(a) == "elite"]
            oportunistas = [a for a in universo if clasificar_trade(a) == "oportunista"]

            # =========================
            # CAPACIDAD
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            # =========================
            # SELECCIÓN
            # =========================
            if espacios > 0:

                seleccion = elite[:espacios]

                if not seleccion:
                    print("⚠️ Usando oportunistas")
                    seleccion = oportunistas[:espacios]

            else:
                print("🔁 Evaluando rotación...")

                candidatos = elite if elite else oportunistas

                if not candidatos:
                    print("⛔ Sin candidatos para rotar")
                    time.sleep(config.CYCLE_TIME)
                    continue

                seleccion = [candidatos[0]]

            # =========================
            # EJECUCIÓN
            # =========================
            ejecutados = 0

            for asset in seleccion:

                ejecutado = portfolio.comprar(
                    asset["symbol"],
                    asset["precio"],
                    asset["prob"],
                    asset["score_final"],
                    precios
                )

                if ejecutado:
                    ejecutados += 1
                    print(
                        f"🟢 TRADE: {asset['symbol']} | "
                        f"prob {round(asset['prob'],2)} | "
                        f"score {round(asset['score_final'],2)}"
                    )

            if ejecutados == 0:
                print("⛔ No se ejecutaron trades")

            # =========================
            # COOLDOWN
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # GUARDADO
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
            print(f"🌐 Universo activo: {len(universo)}")
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