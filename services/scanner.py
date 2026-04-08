import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()

def obtener_datos(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=120)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df

def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 50:
        return None

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["returns"] = df["close"].pct_change()

    precio = float(df["close"].iloc[-1])

    score = 0

    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        score += 1

    if df["returns"].iloc[-1] > 0:
        score += 1

    if df["close"].iloc[-1] > df["ema20"].iloc[-1]:
        score += 1

    # 🔥 PROBABILIDAD MEJORADA
    prob = score / 3

    # filtro anti-ruido
    if df["returns"].iloc[-1] < -0.01:
        prob *= 0.5

    return {
        "symbol": symbol,
        "score": score,
        "prob": float(prob),
        "precio": precio
    }