import config

capital = float(config.CAPITAL_INICIAL)
posiciones = {}

STOP_LOSS = config.STOP_LOSS
TAKE_PROFIT = config.TAKE_PROFIT

# =========================
# ABRIR POSICIÓN (CONTROLADO)
# =========================
def abrir_posicion(symbol, precio, size):
    global capital

    # ❌ evitar recompras infinitas
    if symbol in posiciones:
        return False

    # limitar número de posiciones
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


# =========================
# CERRAR POSICIÓN
# =========================
def cerrar_posicion(symbol, precio):
    global capital

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) * pos["size"]

    capital += pos["size"] * precio

    del posiciones[symbol]

    return pnl


# =========================
# EVALUAR SALIDA (CLAVE)
# =========================
def evaluar_salida(symbol, precio):

    if symbol not in posiciones:
        return False

    pos = posiciones[symbol]
    precio_entrada = pos["precio"]

    pnl = (precio - precio_entrada) / precio_entrada

    # DEBUG
    print(f"🔍 {symbol} pnl: {round(pnl,4)}")

    if pnl <= STOP_LOSS:
        print(f"🛑 STOP LOSS {symbol}")
        return True

    if pnl >= TAKE_PROFIT:
        print(f"🎯 TAKE PROFIT {symbol}")
        return True

    return False


# =========================
# INICIO
# =========================
def cargar_estado():
    global capital
    print("🆕 Iniciando nuevo portfolio")