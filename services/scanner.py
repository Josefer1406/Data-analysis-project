import ccxt
import pandas as pd
import numpy as np
import config

exchange = ccxt.okx()


def obtener_datos(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=100)
        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
        return df
    except:
        return None


def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 50:
        return None

    # =========================
    # INDICADORES
    # =========================
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["returns"] = df["close"].pct_change()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    precio = float(df["close"].iloc[-1])

    # =========================
    # SCORE INTELIGENTE
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

    # RSI saludable (no sobrecompra)
    if 40 < df["rsi"].iloc[-1] < 70:
        score += 1

    # micro tendencia
    if df["close"].iloc[-1] > df["close"].iloc[-5]:
        score += 1

    # =========================
    # PROBABILIDAD (BALANCEADA)
    # =========================
    prob = score / 5

    # =========================
    # FILTRO CALIDAD (🔥 CLAVE)
    # =========================
    if score < 2:
        return None

    if prob < 0.5:
        return None

    # =========================
    # VOLATILIDAD
    # =========================
    volatilidad = df["returns"].std()

    if volatilidad > config.VOLATILIDAD_LIMITE:
        return None

    if volatilidad < config.VOLATILIDAD_MIN:
        return None

    # =========================
    # SALIDA
    # =========================
    return {
        "symbol": symbol,
        "score": score,
        "prob": round(prob, 2),
        "precio": precio,
        "volatilidad": float(volatilidad)
    }