import ccxt
import pandas as pd
import config

exchange = ccxt.bybit({
    "enableRateLimit": True,
    "options": {"defaultType": "spot"}
})

def obtener_datos(symbol):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=config.TIMEFRAME,
        limit=100
    )

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    return df