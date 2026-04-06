from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ml.predictor import predecir
from database import insertar_features
import datetime

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], 14).rsi()

    df["volumen"] = df["volume"]
    df["volatilidad"] = df["close"].pct_change().rolling(10).std()

    df = df.dropna()
    last = df.iloc[-1]

    f = {
        "ema20": last["ema20"],
        "ema50": last["ema50"],
        "rsi": last["rsi"],
        "volumen": last["volumen"],
        "volatilidad": last["volatilidad"]
    }

    insertar_features(datetime.datetime.now(), symbol, f)

    ml = predecir(f)

    trend = 1 if f["ema20"] > f["ema50"] else 0
    rsi = 1 if f["rsi"] < 35 else 0
    momentum = 1 if f["rsi"] > 55 else 0

    score = trend + rsi + momentum

    if ml > 0.65:
        score += 2

    decision = "BUY" if score >= 3 else "HOLD"

    return score, last["close"], decision