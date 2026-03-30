import config

capital = config.CAPITAL_INICIAL
posiciones = {}

STOP_LOSS = -0.02
TAKE_PROFIT = 0.05

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

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) * pos["size"]

    capital += pos["size"] * precio

    del posiciones[symbol]

    return pnl


def evaluar_salida(symbol, precio):

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) / pos["precio"]

    if pnl <= STOP_LOSS or pnl >= TAKE_PROFIT:
        return True

    return False