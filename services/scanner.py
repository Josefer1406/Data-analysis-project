from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import config

def analizar(symbol):

    df = obtener_datos(symbol)

    # =========================
    # INDICADORES DINÁMICOS
    # =========================
    df["ema_fast"] = EMAIndicator(df["close"], window=config.EMA_FAST).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=config.EMA_SLOW).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    last = df.iloc[-1]

    score = 0

    # =========================
    # 1. TENDENCIA
    # =========================
    if last["ema_fast"] > last["ema_slow"]:
        score += 1

    # =========================
    # 2. MOMENTUM
    # =========================
    if config.RSI_LOW < last["rsi"] < config.RSI_HIGH:
        score += 1

    # =========================
    # 3. FUERZA DE TENDENCIA
    # =========================
    fuerza = abs(last["ema_fast"] - last["ema_slow"]) / last["close"]

    if fuerza > 0.01:
        score += 1

    # =========================
    # 4. VOLUMEN
    # =========================
    vol_prom = df["volume"].rolling(20).mean().iloc[-1]

    if last["volume"] > vol_prom:
        score += 1

    return score, last["close"]