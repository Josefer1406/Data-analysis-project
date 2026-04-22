import ccxt
import pandas as pd
import config

exchange = ccxt.okx()


# =========================
# TIMEFRAMES USADOS
# =========================
TIMEFRAMES = ["5m", "15m", "1h"]


def obtener_ohlcv(symbol, timeframe, limit=150):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
        return df
    except Exception as e:
        print(f"❌ Error OHLCV {symbol} {timeframe}: {e}")
        return None


def obtener_multi_timeframe(symbol):

    data = {}

    for tf in TIMEFRAMES:
        df = obtener_ohlcv(symbol, tf)

        if df is None or len(df) < 50:
            return None

        data[tf] = df

    return data


# =========================
# UNIVERSO DINÁMICO (BASE)
# =========================
def obtener_universo():

    # por ahora usamos config
    # luego lo haremos dinámico real (top volumen)

    return config.CRYPTOS