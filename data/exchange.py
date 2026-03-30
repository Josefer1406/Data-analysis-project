import ccxt

# ==========================
# EXCHANGE CONFIG
# ==========================

exchange = ccxt.okx({
    "enableRateLimit": True
})


# ==========================
# OBTENER DATOS MERCADO
# ==========================

def obtener_datos(symbol, timeframe="5m"):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=100
    )

    return ohlcv