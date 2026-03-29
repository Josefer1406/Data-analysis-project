import ccxt

# ===============================
# EXCHANGE CONFIG SEGURO
# ===============================

exchange = ccxt.kucoin({
    'enableRateLimit': True,

    # 🔥 evita congelamientos
    'timeout': 15000,   # 15 segundos máximo

    'options': {
        'adjustForTimeDifference': True
    }
})


# ===============================
# OBTENER DATOS
# ===============================

def obtener_datos(symbol, timeframe):

    try:
        ohlcv = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=100
        )
        return ohlcv

    except Exception as e:
        print(f"[EXCHANGE ERROR] {e}")
        return None