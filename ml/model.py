import random

def analizar_activo(symbol):
    """
    Modelo multi-factor institucional (simulado por ahora)
    """

    tendencia = random.choice([True, False])
    momentum = random.choice([True, False])
    volatilidad = random.choice([True, False])

    score = 0
    if tendencia: score += 1
    if momentum: score += 1
    if volatilidad: score += 1

    probabilidad = score / 3

    return {
        "symbol": symbol,
        "score": score,
        "probabilidad": probabilidad
    }