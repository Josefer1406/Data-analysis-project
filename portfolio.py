import config
import random

capital = config.CAPITAL_INICIAL
posiciones = {}
cooldowns = {}

def capital_disponible():
    return capital * (1 - config.RESERVA_CAPITAL)

def puede_comprar(symbol):
    return symbol not in cooldowns

def actualizar_cooldowns():
    for s in list(cooldowns.keys()):
        cooldowns[s] -= 1
        if cooldowns[s] <= 0:
            del cooldowns[s]

def exposicion_total():
    total = sum(p["inversion"] for p in posiciones.values())
    return total / capital if capital > 0 else 0

def calcular_peso(probabilidad):
    # EXCELENTE
    if probabilidad >= config.UMBRAL_EXCELENTE:
        return config.PESO_EXCELENTE

    # BUENA
    elif probabilidad >= config.UMBRAL_COMPRA:
        return random.uniform(config.PESO_BUENO_MIN, config.PESO_BUENO_MAX)

    return 0

def abrir_posicion(symbol, probabilidad, precio):
    global capital

    if len(posiciones) >= config.MAX_POSICIONES:
        return

    if capital < config.MIN_CAPITAL_OPERAR:
        return

    if exposicion_total() >= config.MAX_EXPOSICION_TOTAL:
        return

    peso = calcular_peso(probabilidad)

    if peso == 0:
        return

    inversion = capital_disponible() * peso

    if inversion <= 0:
        return

    capital -= inversion

    posiciones[symbol] = {
        "inversion": inversion,
        "entry": precio
    }

    print(f"🟢 BUY {symbol} | ${inversion:.2f} | peso: {peso:.2f}")

def cerrar_posicion(symbol, pnl):
    global capital

    inversion = posiciones[symbol]["inversion"]
    capital += inversion * (1 + pnl)

    del posiciones[symbol]
    cooldowns[symbol] = config.COOLDOWN

def gestionar_riesgo():
    for symbol in list(posiciones.keys()):
        entry = posiciones[symbol]["entry"]

        # simulación más realista
        precio_actual = entry * random.uniform(0.97, 1.08)

        pnl = (precio_actual - entry) / entry

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