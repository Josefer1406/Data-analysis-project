from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


# =========================
# FILTRO DE MERCADO (🔥 CLAVE)
# =========================
def mercado_valido(ranking):

    if not ranking:
        return False

    # promedio de probabilidad
    avg_prob = sum([r["prob"] for r in ranking]) / len(ranking)

    # contar activos fuertes
    fuertes = sum(1 for r in ranking if r["prob"] >= config.UMBRAL_BUENO)

    # 🔥 lógica institucional
    if avg_prob < 0.65:
        return False

    if fuertes < 2:
        return False

    return True


def bot():

    print("🚀 BOT HEDGE FUND INICIADO")

    contador = 0

    while True:
        try:
            contador += 1

            print("\n🔎 Analizando mercado...")

            ranking = []
            precios = {}

            # =========================
            # SCAN
            # =========================
            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                if data is None or not isinstance(data, dict):
                    continue

                if "prob" not in data or "precio" not in data or "symbol" not in data:
                    continue

                ranking.append(data)
                precios[symbol] = data["precio"]

            # =========================
            # ACTUALIZAR POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # FILTRO DE MERCADO (🔥 CLAVE)
            # =========================
            if not mercado_valido(ranking):
                print("⛔ Mercado NO favorable (no trade)")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # FILTRO DE CALIDAD
            # =========================
            ranking = [r for r in ranking if r["prob"] >= config.UMBRAL_BUENO]

            if not ranking:
                print("⛔ Sin señales fuertes")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # CONTROL EXPOSICIÓN
            # =========================
            if portfolio.exposicion_actual() >= config.USO_CAPITAL:
                print("⛔ Exposición máxima alcanzada")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # RANKING
            # =========================
            ranking = sorted(ranking, key=lambda x: x["prob"], reverse=True)
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # EJECUCIÓN
            # =========================
            for asset in top:

                try:
                    ejecutado = portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

                    if ejecutado:
                        print(f"🟢 BUY {asset['symbol']} | prob {round(asset['prob'],2)}")

                except Exception as e:
                    print(f"⚠️ Error trade {asset['symbol']}: {e}")

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # GUARDADO
            # =========================
            if contador % 20 == 0:
                portfolio.guardar_resultados()
                print("💾 Resultados guardados")

            # =========================
            # LOGS
            # =========================
            print(f"💰 Capital: {round(portfolio.capital,2)}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
            print(f"📉 Exposición: {round(portfolio.exposicion_actual()*100,2)}%")
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