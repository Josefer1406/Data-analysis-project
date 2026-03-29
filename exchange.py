import ccxt

# ===============================
# EXCHANGE CONFIG - BYBIT TESTNET
# ===============================

exchange = ccxt.bybit({
    'enableRateLimit': True,

    # ⚡ usamos SPOT
    'options': {
        'defaultType': 'spot'
    },

    # 🔥 TESTNET (modo simulación)
    'urls': {
        'api': {
            'public': 'https://api-testnet.bybit.com',
            'private': 'https://api-testnet.bybit.com'
        }
    }
})


# ===============================
# OBTENER DATOS DE MERCADO
# ===============================

def obtener_datos(symbol, timeframe):
    """
    Descarga velas OHLCV desde Bybit Testnet
    """
    ohlcv = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=100
    )

    return ohlcv