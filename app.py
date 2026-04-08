from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


def bot():

    print("🚀 BOT INSTITUCIONAL INICIADO")

    contador = 0  # 🔥 guardado automático

    while True:
        try:
            contador += 1

            print("\n🔎 Analizando mercado...")

            ranking = []
            precios = {}

            # =========================
            # SCAN PROFESIONAL
            # =========================
            for symbol in config.CRYPTOS:

                data = analizar(symbol)

                # 🔥 PROTECCIÓN TOTAL (evita errores)
                if data is None or not isinstance(data, dict):
                    continue

                # validar estructura mínima
                if "prob" not in data or "precio" not in data or "symbol" not in data:
                    continue

                # 🔥 FILTRO ANTI BASURA
                if data["prob"] < config.UMBRAL_BUENO:
                    continue

                ranking.append(data)
                precios[symbol] = data["precio"]

            # =========================
            # ACTUALIZAR POSICIONES
            # =========================
            portfolio.actualizar(precios)

            # =========================
            # CONTROL DE EXPOSICIÓN (HEDGE FUND)
            # =========================
            if portfolio.exposicion_actual() >= config.USO_CAPITAL:
                print("⛔ Exposición máxima alcanzada")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # NO OPERAR SI NO HAY EDGE
            # =========================
            if not ranking:
                print("⛔ Sin oportunidades reales")
                time.sleep(config.CYCLE_TIME)
                continue

            # =========================
            # RANKING (MEJORES PRIMERO)
            # =========================
            ranking = sorted(ranking, key=lambda x: x["prob"], reverse=True)

            # 🔥 SOLO TOP INSTITUCIONAL
            top = ranking[:config.MAX_POSICIONES]

            # =========================
            # EJECUCIÓN CONTROLADA
            # =========================
            for asset in top:

                try:
                    ejecutado = portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

                    if ejecutado:
                        print(f"🟢 Compra ejecutada: {asset['symbol']} | prob: {round(asset['prob'],2)}")

                except Exception as e:
                    print(f"⚠️ Error ejecutando trade {asset['symbol']}: {e}")

            # =========================
            # COOLDOWN DINÁMICO
            # =========================
            portfolio.actualizar_cooldown()

            # =========================
            # GUARDADO AUTOMÁTICO
            # =========================
            if contador % 20 == 0:
                try:
                    portfolio.guardar_resultados()
                    print("💾 Resultados guardados")
                except Exception as e:
                    print(f"⚠️ Error guardando resultados: {e}")

            # =========================
            # LOGS PROFESIONALES
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