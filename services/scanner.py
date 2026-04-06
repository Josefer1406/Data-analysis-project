from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ml.predictor import predecir

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], 14).rsi()

    df["volumen"] = df["volume"]
    df["volatilidad"] = df["close"].pct_change().rolling(10).std()

    df = df.dropna()
    last = df.iloc[-1]

    features = {
        "ema20": last["ema20"],
        "ema50": last["ema50"],
        "rsi": last["rsi"],
        "volumen": last["volumen"],
        "volatilidad": last["volatilidad"]
    }

    prob = predecir(features)

    score = 0

    if last["ema20"] > last["ema50"]:
        score += 1

    if 40 < last["rsi"] < 60:
        score += 1

    if prob > 0.6:
        score += 2

    decision = "BUY" if score >= 3 else "HOLD"

    return score, last["close"], decision, prob