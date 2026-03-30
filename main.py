import time
import config

from services.scanner import escanear
from core.risk import calcular_size
from filters.market_filter import mercado_favorable

import portfolio
import logger

print("🤖 BOT OPTIMIZADO INICIADO")

while True:

    try:

        # 🚫 NO OPERAR SI MERCADO MALO
        if not mercado_favorable():
            print("❌ Mercado no favorable")
            time.sleep(60)
            continue

        for symbol in config.CRYPTOS:

            signal, precio = escanear(symbol)

            # 📊 REVISAR SALIDAS
            cerrar = portfolio.revisar_posiciones(precio)

            for s in cerrar:
                pnl = portfolio.cerrar_posicion(s, precio)
                logger.log_trade(s, "SELL", precio, 0, pnl)
                print(f"🔴 Cierre {s} PnL {pnl}")

            # 🟢 ENTRADA
            if signal == "BUY":

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