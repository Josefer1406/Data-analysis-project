from data.exchange import obtener_datos
from ta.trend import EMAIndicator
import pandas as pd
import config


def mercado_favorable():

    print("🌎 Analizando mercado global...")

    ohlcv = obtener_datos("BTC/USDT", config.TIMEFRAME)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()

    last = df.iloc[-1]

    # REGIMEN DE MERCADO
    if last["ema50"] > last["ema200"]:
        print("✅ Mercado alcista detectado")
        return True
    else:
        print("❌ Mercado bajista — NO OPERAR")
        return False