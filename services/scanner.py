import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()


def obtener_datos(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=150)
        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
        return df
    except:
        return None


def calcular_rsi(df, period=14):
    delta = df["close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 100:
        return None

    # =========================
    # INDICADORES
    # =========================
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()
    df["rsi"] = calcular_rsi(df)
    df["returns"] = df["close"].pct_change()

    precio = float(df["close"].iloc[-1])
    rsi = float(df["rsi"].iloc[-1])

    # =========================
    # VOLATILIDAD
    # =========================
    volatilidad = df["returns"].std()

    if volatilidad > config.VOLATILIDAD_LIMITE:
        return None

    if volatilidad < config.VOLATILIDAD_MIN:
        return None

    # =========================
    # SCORE PROFESIONAL
    # =========================
    score = 0

    # tendencia fuerte
    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        score += 1

    # precio por encima de tendencia
    if precio > df["ema20"].iloc[-1]:
        score += 1

    # momentum real
    if df["returns"].iloc[-1] > 0:
        score += 1

    # RSI sano
    if 45 < rsi < 70:
        score += 1

    # =========================
    # PROBABILIDAD REALISTA
    # =========================
    prob_map = {
        0: 0.2,
        1: 0.45,
        2: 0.65,
        3: 0.80,
        4: 0.92
    }

    prob = prob_map.get(score, 0.2)

    # =========================
    # FILTRO FINAL (EDGE)
    # =========================
    if score < 3:
        return None

    return {
        "symbol": symbol,
        "score": score,
        "prob": prob,
        "precio": precio,
        "volatilidad": float(volatilidad),
        "rsi": rsi
    }