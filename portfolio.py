import config
import random

capital = config.CAPITAL_INICIAL
posiciones = {}
cooldowns = {}

def capital_disponible():
    return capital * (1 - config.RESERVA_CAPITAL)

def puede_comprar(symbol):
    if symbol in cooldowns and cooldowns[symbol] > 0:
        return False
    return True

def actualizar_cooldowns():
    for s in list(cooldowns.keys()):
        cooldowns[s] -= 1
        if cooldowns[s] <= 0:
            del cooldowns[s]

def exposicion_total():
    total = sum(p["inversion"] for p in posiciones.values())
    return total / capital if capital > 0 else 0

def abrir_posicion(symbol, probabilidad):
    global capital

    if len(posiciones) >= config.MAX_POSICIONES:
        return

    if capital < config.MIN_CAPITAL_OPERAR:
        return

    if exposicion_total() >= config.MAX_EXPOSICION_TOTAL:
        return

    # Position sizing institucional
    if probabilidad >= config.UMBRAL_COMPRA_FUERTE:
        peso = config.MAX_PESO_POR_ACTIVO
    else:
        peso = config.MIN_PESO_POR_ACTIVO

    inversion = capital_disponible() * peso

    if inversion <= 0:
        return

    capital -= inversion

    posiciones[symbol] = {
        "inversion": inversion,
        "entry": 1.0
    }

    print(f"🟢 BUY {symbol} | ${inversion:.2f}")

def cerrar_posicion(symbol, pnl):
    global capital

    inversion = posiciones[symbol]["inversion"]
    capital += inversion * (1 + pnl)

    del posiciones[symbol]
    cooldowns[symbol] = config.COOLDOWN

def gestionar_riesgo():
    for symbol in list(posiciones.keys()):
        pnl = random.uniform(-0.05, 0.08)

        print(f"🔍 {symbol} pnl: {pnl:.4f}")

        if pnl <= config.STOP_LOSS:
            print(f"🔴 STOP LOSS {symbol}")
            cerrar_posicion(symbol, pnl)

        elif pnl >= config.TAKE_PROFIT:
            print(f"💰 TAKE PROFIT {symbol}")
            cerrar_posicion(symbol, pnl)

def estado():
    print(f"💰 Capital: {round(capital, 2)}")
    print(f"📊 Posiciones: {list(posiciones.keys())}")