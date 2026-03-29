import config
import exchange

def escanear_mercado():

    oportunidades = []

    for symbol in config.CRYPTOS:

        precio = exchange.obtener_precio(symbol)

        if precio is None:
            continue

        print(f"🔎 Analizando {symbol} | Precio: {precio}")

        # Estrategia SIMPLE (demo)
        if precio > 0:
            oportunidades.append({
                "symbol": symbol,
                "precio": precio
            })

    return oportunidades