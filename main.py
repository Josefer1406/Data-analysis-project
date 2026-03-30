import time
import config

from filters.market_filter import mercado_favorable
from services.scanner import analizar
from core.risk import calcular_size

import portfolio
import logger

print("🤖 BOT EXPERTO INICIADO")

while True:

    try:

        if not mercado_favorable():
            print("⛔ No operar")
            time.sleep(60)
            continue

        ranking = []

        for symbol in config.CRYPTOS:

            score, precio = analizar(symbol)

            ranking.append((symbol, score, precio))

        # 🔥 ORDENAR MEJORES
        ranking.sort(key=lambda x: x[1], reverse=True)

        mejor = ranking[0]

        symbol, score, precio = mejor

        print(f"🏆 Mejor activo: {symbol} | Score {score}")

        # 🔴 SALIDAS
        for s in list(portfolio.posiciones.keys()):
            if portfolio.evaluar_salida(s, precio):
                pnl = portfolio.cerrar_posicion(s, precio)
                logger.log_trade(s, "SELL", precio, 0, pnl)
                print(f"🔴 Cierre {s} PnL {pnl}")

        # 🟢 ENTRADA
        if score >= 2:

            size = calcular_size(precio)

            if portfolio.abrir_posicion(symbol, precio, size):
                logger.log_trade(symbol, "BUY", precio, size, 0)
                print(f"🟢 Compra {symbol}")

        print(f"💰 Capital: {portfolio.capital}")
        print("⏳ Esperando...\n")

        time.sleep(config.CYCLE_TIME)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)