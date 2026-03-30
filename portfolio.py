import config

capital = config.CAPITAL_INICIAL
posiciones = {}

STOP_LOSS = -0.02
TAKE_PROFIT = 0.04

def abrir_posicion(symbol, precio, size):

    global capital

    if symbol in posiciones:
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


def revisar_posiciones(precio_actual):

    cerrar = []

    for symbol, pos in posiciones.items():

        pnl = (precio_actual - pos["precio"]) / pos["precio"]

        if pnl <= STOP_LOSS or pnl >= TAKE_PROFIT:
            cerrar.append(symbol)

    return cerrar


def cerrar_posicion(symbol, precio):

    global capital

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) * pos["size"]

    capital += pos["size"] * precio

    del posiciones[symbol]

    return pnl