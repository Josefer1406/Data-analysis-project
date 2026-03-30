import time
import config

from filters.market_filter import mercado_favorable
from services.scanner import analizar
from core.risk import calcular_size

import portfolio
import logger
import adaptive

print("🤖 BOT ELITE INICIADO")

while True:

    try:
        estado = mercado_favorable()

        # IA SIMPLE (adaptive)
        MIN_SCORE = adaptive.calcular_min_score()

        print(f"🧠 MIN_SCORE dinámico: {MIN_SCORE}")

        ranking = []

        for symbol in config.CRYPTOS:
            score, precio = analizar(symbol)
            ranking.append((symbol, score, precio))

        ranking.sort(key=lambda x: x[1], reverse=True)

        top = ranking[:config.MAX_POSICIONES]

        print("\n🏆 Ranking:")

        for s, sc, p in top:
            print(f"{s} | Score {sc}")

        # SALIDAS
        for s in list(portfolio.posiciones.keys()):
            precio_actual = next((p for sym, sc, p in ranking if sym == s), None)

            if precio_actual and portfolio.evaluar_salida(s, precio_actual):
                pnl = portfolio.cerrar_posicion(s, precio_actual)
                logger.log_trade(s, "SELL", precio_actual, 0, pnl)
                print(f"🔴 Cierre {s} PnL {pnl}")

        # ENTRADAS
        for s, sc, p in top:
            if sc >= MIN_SCORE:
                size = calcular_size(p)

                if portfolio.abrir_posicion(s, p, size):
                    logger.log_trade(s, "BUY", p, size, 0)
                    print(f"🟢 Compra {s}")

        print(f"\n💰 Capital: {portfolio.capital}")
        print(f"📊 Posiciones: {list(portfolio.posiciones.keys())}")
        print("⏳ Esperando...\n")

        time.sleep(config.CYCLE_TIME)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)