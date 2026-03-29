from data.exchange import obtener_datos
from core.strategy import aplicar_estrategia, evaluar
import config

def escanear_mercado():

    oportunidades = []

    for symbol in config.CRYPTOS:

        print(f"Escaneando {symbol}")

        df = obtener_datos(symbol)

        df = aplicar_estrategia(df)

        señal = evaluar(df)

        if señal == "BUY":
            oportunidades.append((symbol, df["close"].iloc[-1]))

    return oportunidades