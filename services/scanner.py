from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import pandas as pd
import config


def escanear_mercado():

    oportunidades = []

    for symbol in config.CRYPTOS:

        print(f"Escaneando {symbol}")

        ohlcv = obtener_datos(symbol, config.TIMEFRAME)

        df = pd.DataFrame(
            ohlcv,
            columns=["time","open","high","low","close","volume"]
        )

        df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
        df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
        df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

        last = df.iloc[-1]

        if last["ema20"] > last["ema50"] and last["rsi"] < 40:
            oportunidades.append((symbol, last["close"]))

    return oportunidades