from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import numpy as np

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], 14).rsi()
    df["ret"] = df["close"].pct_change()

    df = df.dropna()
    last = df.iloc[-1]

    # FEATURES
    X = np.array([[last["ema20"], last["ema50"], last["rsi"], last["ret"]]])

    # SCORE BASE
    score = 0
    if last["ema20"] > last["ema50"]:
        score += 1
    if last["rsi"] < 40:
        score += 1

    return symbol, score, X, last["close"]