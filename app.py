from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


def bot():

    print("🚀 BOT HEDGE FUND REAL ACTIVADO")

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
                candidatos.append(data)

            # actualizar posiciones
            portfolio.actualizar(precios)

            # ordenar mejores
            candidatos = sorted(candidatos, key=lambda x: x["prob"], reverse=True)

            # =========================
            # ROTACIÓN FORZADA
            # =========================
            if len(portfolio.posiciones) > 0 and candidatos:

                mejor = candidatos[0]

                peor_symbol = None
                peor_prob = 1

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_prob:
                        peor_prob = pos["prob"]
                        peor_symbol = s

                if mejor["prob"] > peor_prob + 0.1:
                    print(f"🔄 ROTANDO {peor_symbol} → {mejor['symbol']}")

                    portfolio.cerrar(peor_symbol, precios.get(peor_symbol, 0), 0)

                    portfolio.comprar(
                        mejor["symbol"],
                        mejor["precio"],
                        mejor["prob"]
                    )

            # =========================
            # ABRIR NUEVAS POSICIONES
            # =========================
            espacios = config.MAX_POSICIONES - len(portfolio.posiciones)

            if espacios > 0:
                nuevos = candidatos[:espacios]

                for asset in nuevos:
                    portfolio.comprar(
                        asset["symbol"],
                        asset["precio"],
                        asset["prob"]
                    )

            # cooldown
            portfolio.actualizar_cooldown()

            print(f"💰 Capital: {portfolio.capital}")
            print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")

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