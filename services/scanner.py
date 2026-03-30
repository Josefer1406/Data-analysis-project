from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ml.predictor import predecir

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    last = df.iloc[-1]

    # ML predicción
    prob = predecir(df)

    score = 0

    if last["ema20"] > last["ema50"]:
        score += 1

    if 30 < last["rsi"] < 50:
        score += 1

    # ML como factor clave
    if prob > 0.6:
        score += 2

    return score, last["close"]