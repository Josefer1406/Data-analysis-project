import scanner
import risk
import logger
import exchange
import time

print("BOT PROFESIONAL INICIADO")

while True:

    oportunidades = scanner.escanear_mercado()

    for symbol, señal in oportunidades:

        ticker = exchange.exchange.fetch_ticker(symbol)
        precio = ticker["last"]

        size = risk.calcular_size(precio)

        print(f"{señal} -> {symbol} | Precio: {precio}")

        logger.guardar_trade(symbol, señal, precio, size)

    time.sleep(60)