import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()


def obtener_datos(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=100)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df


def calcular_rsi(series, period=14):
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 50:
        return None

    # =========================
    # FEATURES
    # =========================
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["returns"] = df["close"].pct_change()
    df["rsi"] = calcular_rsi(df["close"])

    precio = float(df["close"].iloc[-1])
    rsi = float(df["rsi"].iloc[-1])

    # =========================
    # SCORE MEJORADO
    # =========================
    score = 0

    # tendencia
    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        score += 1

    # momentum
    if df["returns"].iloc[-1] > 0:
        score += 1

    # confirmación
    if df["close"].iloc[-1] > df["ema20"].iloc[-1]:
        score += 1

    # RSI saludable (🔥 clave)
    if 45 < rsi < 70:
        score += 1

    # =========================
    # PROBABILIDAD MEJORADA
    # =========================
    prob_map = {
        0: 0.2,
        1: 0.45,
        2: 0.65,
        3: 0.80,
        4: 0.90
    }

    prob = prob_map.get(score, 0.2)

    # =========================
    # VOLATILIDAD AJUSTADA
    # =========================
    volatilidad = df["returns"].std()

    if volatilidad > config.VOLATILIDAD_LIMITE:
        return None

    if volatilidad < (config.VOLATILIDAD_MIN * 0.5):
        return None

    # =========================
    # SALIDA
    # =========================
    return {
        "symbol": symbol,
        "score": score,
        "prob": prob,
        "precio": precio,
        "volatilidad": float(volatilidad),
        "rsi": rsi
    }