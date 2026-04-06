from data.exchange import obtener_datos
from ta.trend import EMAIndicator

def mercado_favorable():
    try:
        df = obtener_datos("BTC/USDT")

        df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
        df["ema200"] = EMAIndicator(df["close"], 200).ema_indicator()

        df = df.dropna()
        last = df.iloc[-1]

        # mercado alcista
        return last["ema50"] > last["ema200"]

    except Exception as e:
        print(f"Error filtro mercado: {e}")
        return False