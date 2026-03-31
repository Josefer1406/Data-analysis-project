from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

from ml.predictor import predecir

def analizar(symbol):

    df = obtener_datos(symbol)

    # =========================
    # INDICADORES BASE
    # =========================
    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    # =========================
    # FEATURES AVANZADAS (ML)
    # =========================
    df["return"] = df["close"].pct_change()
    df["volatility"] = df["return"].rolling(10).std()
    df["momentum"] = df["close"] - df["close"].shift(5)

    df = df.dropna()

    if df.empty:
        return 0, 0

    last = df.iloc[-1]

    # =========================
    # PREDICCIÓN ML
    # =========================
    prob = predecir(df)

    score = 0

    # =========================
    # 1. TENDENCIA
    # =========================
    if last["ema20"] > last["ema50"]:
        score += 1

    # =========================
    # 2. MOMENTUM (RSI)
    # =========================
    if 30 < last["rsi"] < 60:
        score += 1

    # =========================
    # 3. FUERZA DE TENDENCIA
    # =========================
    fuerza = abs(last["ema20"] - last["ema50"]) / last["close"]

    if fuerza > 0.01:
        score += 1

    # =========================
    # 4. VOLUMEN
    # =========================
    vol_prom = df["volume"].rolling(20).mean().iloc[-1]

    if last["volume"] > vol_prom:
        score += 1

    # =========================
    # 5. MACHINE LEARNING (PESO ALTO)
    # =========================
    if prob > 0.65:
        score += 2
    elif prob > 0.55:
        score += 1

    return score, last["close"]