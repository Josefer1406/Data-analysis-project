from data.exchange import obtener_datos
from ta.trend import EMAIndicator

def mercado_favorable():
    print("🌎 Analizando BTC...")

    df = obtener_datos("BTC/USDT")

    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()

    last = df.iloc[-1]

    if last["ema50"] > last["ema200"]:
        print("🚀 Mercado alcista")
        return "ALCISTA"
    else:
        print("⚠️ Mercado débil")
        return "DEBIL"