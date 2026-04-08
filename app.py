from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


def score_institucional(asset):
    """
    🧠 SCORING REAL TIPO HEDGE FUND
    """

    prob = asset["prob"]
    score = asset["score"]

    # base
    s = prob * 0.6 + (score / 3) * 0.4

    # bonus por excelencia
    if prob > 0.9:
        s += 0.1

    return s


def filtro_calidad(asset):
    """
    🔥 FILTRO ULTRA SELECTIVO
    """

    if asset["prob"] < 0.82:
        return False

    if asset["score"] < 2:
        return False

    if asset["precio"] <= 0:
        return False

    return True


def bot():

    print("🚀 BOT HEDGE FUND ULTRA ACTIVADO")

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

                # 🔥 añadir score institucional
                data["score_final"] = score_institucional(data)

                candidatos.append(data)

            # =========================
            # GESTIÓN POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # SIN EDGE
            # =========================
            if len(candidatos) == 0:
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
            # CAPACIDAD
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios <= 0:
                print("📊 Portafolio lleno")
                time.sleep(config.CYCLE_TIME)
                continue

            # 🔥 SOLO LOS MEJORES DE VERDAD
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
            print(f"📈 Candidatos reales: {len(candidatos)}")
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