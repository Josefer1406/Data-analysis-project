from flask import Flask, jsonify
import threading
import time
import config

from services.scanner import analizar
from portfolio import portfolio

app = Flask(__name__)


def score(asset):
    return (asset["prob"] * 0.65) + ((asset["score"] / 5) * 0.35)


def clasificar(asset):

    if asset["prob"] >= 0.75 and asset["score"] >= 3:
        return "elite"

    if asset["prob"] >= 0.60 and asset["score"] >= 2:
        return "buena"

    return None


def correlacionado(symbol, posiciones):

    grupo_nuevo = None

    for g, lista in config.CORRELACION.items():
        if symbol in lista:
            grupo_nuevo = g
            break

    for s in posiciones:
        for g, lista in config.CORRELACION.items():
            if s in lista and g == grupo_nuevo:
                return True

    return False


def bot():

    print("🚀 BOT FINAL ACTIVADO")

    while True:
        try:

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

            portfolio.actualizar(precios)

            candidatos = sorted(candidatos, key=lambda x: x["score_final"], reverse=True)

            # ROTACIÓN
            if portfolio.posiciones and candidatos:

                mejor = candidatos[0]

                peor_symbol = None
                peor_prob = 999

                for s, pos in portfolio.posiciones.items():
                    if pos["prob"] < peor_prob:
                        peor_prob = pos["prob"]
                        peor_symbol = s

                if mejor["prob"] > peor_prob + 0.05:
                    portfolio.cerrar(peor_symbol, precios.get(peor_symbol, 0), 0)

            capital_operable = portfolio.capital * config.USO_CAPITAL

            for asset in candidatos:

                if len(portfolio.posiciones) >= config.MAX_POSICIONES:
                    break

                if asset["symbol"] in portfolio.posiciones:
                    continue

                if correlacionado(asset["symbol"], portfolio.posiciones):
                    continue

                if asset["tipo"] == "elite":
                    inversion = capital_operable * 0.15
                else:
                    inversion = capital_operable * 0.10

                portfolio.comprar(
                    asset["symbol"],
                    asset["precio"],
                    asset["prob"],
                    inversion
                )

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