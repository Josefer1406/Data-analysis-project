import time
import config

from services.scanner import escanear
from core.risk import calcular_size
import portfolio
import logger

print("🤖 BOT PAPER TRADING REAL INICIADO")

while True:

    try:

        for symbol in config.CRYPTOS:

            signal, precio = escanear(symbol)

            if signal == "BUY":

                size = calcular_size(precio)

                if portfolio.abrir_posicion(symbol, precio, size):

                    print(f"🟢 COMPRA {symbol} {precio}")

                    logger.log_trade(symbol, "BUY", precio, size, 0)

            elif signal == "SELL":

                pnl = portfolio.cerrar_posicion(symbol, precio)

                if pnl != 0:

                    print(f"🔴 VENTA {symbol} PnL: {pnl}")

                    logger.log_trade(symbol, "SELL", precio, 0, pnl)

        print(f"💰 Capital actual: {portfolio.capital}")
        print("⏳ Esperando próximo ciclo...\n")

        time.sleep(config.CYCLE_TIME)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)