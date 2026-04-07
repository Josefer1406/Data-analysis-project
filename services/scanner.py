import ccxt
import pandas as pd
import config

exchange = ccxt.okx()

def obtener_datos(symbol):

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=config.TIMEFRAME, limit=100)

    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

    return df


def analizar(symbol):

    df = obtener_datos(symbol)

    if df is None or len(df) < 50:
        return 0, 0, "HOLD", 0

    # =========================
    # INDICADORES
    # =========================
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    df["returns"] = df["close"].pct_change()

    precio = df["close"].iloc[-1]

    score = 0

    # =========================
    # SEÑALES
    # =========================
    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        score += 1

    if df["returns"].iloc[-1] > 0:
        score += 1

    if df["close"].iloc[-1] > df["ema20"].iloc[-1]:
        score += 1

    # =========================
    # PROBABILIDAD REAL
    # =========================
    prob = score / 3  # 0 → 1

    if score >= 2:
        decision = "BUY"
    else:
        decision = "HOLD"

    return score, precio, decision, prob