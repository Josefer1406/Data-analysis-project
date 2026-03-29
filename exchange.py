import ccxt

print("[EXCHANGE] Conectando a exchange público...")

exchange = ccxt.okx({
    "enableRateLimit": True,
})

def obtener_precio(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except Exception as e:
        print(f"[EXCHANGE ERROR] {e}")
        return None