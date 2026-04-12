import ccxt
import pandas as pd
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

    if df["returns"].iloc[-5:].mean() > 0:
        score += 1

    if df["ema20"].iloc[-1] > df["ema20"].iloc[-5]:
        score += 1

    prob = score / 5

    volatilidad = df["returns"].std()

    if volatilidad > config.VOLATILIDAD_LIMITE:
        return None

    if volatilidad < config.VOLATILIDAD_MIN:
        return None

    return {
        "symbol": symbol,
        "score": score,
        "prob": prob,
        "precio": precio,
        "volatilidad": float(volatilidad)
    }