import config
import exchange
import strategy

def escanear_mercado():

    oportunidades = []

    for symbol in config.CRYPTOS:

        data = exchange.obtener_datos(symbol, config.TIMEFRAME)

        df = strategy.calcular_indicadores(data)

        señal = strategy.generar_senal(df)

        if señal != "HOLD":
            oportunidades.append((symbol, señal))

    return oportunidades