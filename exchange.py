import ccxt
import config

exchange = ccxt.bybit({
    'enableRateLimit': True
})

def obtener_datos(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    return ohlcv