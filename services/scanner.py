import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()


def obtener_datos(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=100)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df


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

    precio = float(df["close"].iloc[-1])

    # =========================
    # SCORE
    # =========================
    score = 0

    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        score += 1

    if df["returns"].iloc[-1] > 0:
        score += 1

    if df["close"].iloc[-1] > df["ema20"].iloc[-1]:
        score += 1

    # =========================
    # PROBABILIDAD (NO LINEAL)
    # =========================
    prob_map = {
        0: 0.1,
        1: 0.4,
        2: 0.7,
        3: 0.85
    }

    prob = prob_map.get(score, 0.1)

    # =========================
    # VOLATILIDAD (FILTRO)
    # =========================
    volatilidad = df["returns"].std()

    if volatilidad > config.VOLATILIDAD_LIMITE:
        return None

    if volatilidad < config.VOLATILIDAD_MIN:
        return None

    # =========================
    # SALIDA ESTÁNDAR (CLAVE)
    # =========================
    return {
        "symbol": symbol,
        "score": score,
        "prob": prob,
        "precio": precio,
        "volatilidad": float(volatilidad)
    }