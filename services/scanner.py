from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import numpy as np

from ml.predictor import predecir
from core.strategies import (
    trend_following,
    mean_reversion,
    momentum,
    volatility_filter
)
from core.ensemble import decision_ensemble

def analizar(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    df["volumen"] = df["volume"]
    df["volatilidad"] = df["close"].pct_change().rolling(10).std()

    df = df.dropna()

    last = df.iloc[-1]

    # =========================
    # ML
    # =========================
    features = {
        "ema20": last["ema20"],
        "ema50": last["ema50"],
        "rsi": last["rsi"],
        "volumen": last["volumen"],
        "volatilidad": last["volatilidad"]
    }

    ml_prob = predecir(features)

    # =========================
    # ESTRATEGIAS
    # =========================
    signals = [
        trend_following(last),
        mean_reversion(last),
        momentum(last),
        volatility_filter(last)
    ]

    decision = decision_ensemble(signals, ml_prob)

    score = sum(signals)

    return score, last["close"], decision