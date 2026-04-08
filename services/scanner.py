import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()

def obtener_datos(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=100)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df


def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 50:
        return 0, 0, 0, 0

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["returns"] = df["close"].pct_change()
    df["volatilidad"] = df["returns"].rolling(10).std()

    precio = df["close"].iloc[-1]
    vol = df["volatilidad"].iloc[-1]

    score = 0

    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        score += 1

    if df["returns"].iloc[-1] > 0:
        score += 1

    if precio > df["ema20"].iloc[-1]:
        score += 1

    # PROBABILIDAD REALISTA (sin 1.0)
    prob = 0.4 + (score * 0.18)

    # penalizar alta volatilidad
    if vol > config.VOLATILIDAD_LIMITE:
        prob *= 0.7

    prob = min(prob, 0.95)

    return score, precio, prob, vol