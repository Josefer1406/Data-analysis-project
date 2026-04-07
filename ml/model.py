import random

# Estado interno del "mercado simulado"
estado_mercado = {}

def generar_estado(symbol):
    if symbol not in estado_mercado:
        estado_mercado[symbol] = {
            "tendencia": random.choice([-1, 1]),
            "fuerza": random.uniform(0.3, 1.0),
            "persistencia": random.randint(3, 8)
        }

def actualizar_estado(symbol):
    estado = estado_mercado[symbol]

    estado["persistencia"] -= 1

    # Cambio de régimen (como mercado real)
    if estado["persistencia"] <= 0:
        estado["tendencia"] = random.choice([-1, 1])
        estado["fuerza"] = random.uniform(0.3, 1.0)
        estado["persistencia"] = random.randint(3, 8)

def analizar_activo(symbol):
    generar_estado(symbol)
    actualizar_estado(symbol)

    estado = estado_mercado[symbol]

    # Factores tipo institucional
    tendencia = estado["tendencia"] == 1
    momentum = estado["fuerza"] > 0.6
    volatilidad = estado["fuerza"] > 0.4

    score = 0

    if tendencia:
        score += 1
    if momentum:
        score += 1
    if volatilidad:
        score += 1

    probabilidad = score / 3

    return {
        "symbol": symbol,
        "score": score,
        "probabilidad": probabilidad
    }