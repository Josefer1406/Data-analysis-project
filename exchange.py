import ccxt
import config

exchange = ccxt.binance({
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET,
    "enableRateLimit": True
})

def obtener_datos(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    return ohlcv