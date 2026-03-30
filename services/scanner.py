from data.exchange import obtener_datos
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import config

def escanear(symbol):

    df = obtener_datos(symbol)

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    last = df.iloc[-1]

    # 🧠 FILTRO DE TENDENCIA
    tendencia = last["ema20"] > last["ema50"]

    # 🎯 ENTRADA INTELIGENTE (pullback)
    entrada = last["rsi"] < 40

    if tendencia and entrada:
        return "BUY", last["close"]

    if last["rsi"] > 70:
        return "SELL", last["close"]

    return None, last["close"]