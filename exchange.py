import ccxt

# ===============================
# KUCOIN EXCHANGE (RECOMENDADO)
# ===============================

exchange = ccxt.kucoin({
    'enableRateLimit': True,
})


# ===============================
# OBTENER DATOS DE MERCADO
# ===============================

def obtener_datos(symbol, timeframe):

    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=100
    )

    return ohlcv