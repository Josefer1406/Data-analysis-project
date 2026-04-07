import config

capital = float(config.CAPITAL_INICIAL)
posiciones = {}

STOP_LOSS = config.STOP_LOSS
TAKE_PROFIT = config.TAKE_PROFIT


def capital_disponible():
    return capital * (1 - config.RESERVA_CAPITAL)


def abrir_posicion(symbol, precio, size):
    global capital

    # 🔥 BLOQUEO CRÍTICO
    if symbol in posiciones:
        return False

    if len(posiciones) >= config.MAX_POSICIONES:
        return False

    costo = precio * size

    if costo > capital_disponible():
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

    if symbol not in posiciones:
        return False

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) / pos["precio"]

    print(f"🔍 {symbol} pnl: {round(pnl,4)}")

    if pnl <= STOP_LOSS:
        print(f"🛑 STOP LOSS {symbol}")
        return True

    if pnl >= TAKE_PROFIT:
        print(f"🎯 TAKE PROFIT {symbol}")
        return True

    return False


def cargar_estado():
    global capital

    if capital < config.MIN_CAPITAL_OPERAR:
        print("⚠️ Capital bajo, reiniciando")
        capital = config.CAPITAL_INICIAL

    print(f"💰 Capital inicial: {capital}")