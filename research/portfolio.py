import config

capital = config.CAPITAL_INICIAL

posiciones = {}

def abrir_posicion(symbol, precio, size):

    global capital

    if symbol in posiciones:
        return False

    if len(posiciones) >= config.MAX_POSICIONES:
        return False

    costo = precio * size

    if costo > capital:
        return False

    capital -= costo

    posiciones[symbol] = {
        "precio": precio,
        "size": size
    }

    return True


def cerrar_posicion(symbol, precio):

    global capital

    if symbol not in posiciones:
        return 0

    entrada = posiciones[symbol]

    pnl = (precio - entrada["precio"]) * entrada["size"]

    capital += entrada["size"] * precio

    del posiciones[symbol]

    return pnl