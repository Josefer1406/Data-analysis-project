from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    last = df.iloc[-1]

    score = 0

    # tendencia
    if last["ema20"] > last["ema50"]:
        score += 1

    # momentum
    if 30 < last["rsi"] < 50:
        score += 1

    # fuerza
    fuerza = abs(last["ema20"] - last["ema50"]) / last["close"]
    if fuerza > 0.01:
        score += 1

    # volumen
    vol_prom = df["volume"].rolling(20).mean().iloc[-1]
    if last["volume"] > vol_prom:
        score += 1

    return score, last["close"]