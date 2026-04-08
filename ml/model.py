import random

mercado = {}

def init_symbol(symbol):
    if symbol not in mercado:
        precio_inicial = random.uniform(50, 50000)

        mercado[symbol] = {
            "precio": precio_inicial,
            "historial": [precio_inicial],
            "tendencia": random.choice([-1, 1]),
            "volatilidad": random.uniform(0.001, 0.02),
            "persistencia": random.randint(5, 15)
        }

def simular_precio(symbol):
    data = mercado[symbol]

    data["persistencia"] -= 1
    if data["persistencia"] <= 0:
        data["tendencia"] = random.choice([-1, 1])
        data["volatilidad"] = random.uniform(0.001, 0.02)
        data["persistencia"] = random.randint(5, 15)

    drift = data["tendencia"] * data["volatilidad"]
    ruido = random.uniform(-data["volatilidad"], data["volatilidad"])

    cambio = drift + ruido
    data["precio"] *= (1 + cambio)

    data["historial"].append(data["precio"])
    if len(data["historial"]) > 100:
        data["historial"].pop(0)

def calcular_ema(valores, periodo):
    if len(valores) < periodo:
        return valores[-1]

    k = 2 / (periodo + 1)
    ema = valores[0]

    for v in valores[1:]:
        ema = v * k + ema * (1 - k)

    return ema

def calcular_rsi(valores, periodo=14):
    if len(valores) < periodo + 1:
        return 50

    ganancias = []
    perdidas = []

    for i in range(1, periodo + 1):
        cambio = valores[-i] - valores[-i - 1]
        if cambio > 0:
            ganancias.append(cambio)
        else:
            perdidas.append(abs(cambio))

    avg_gain = sum(ganancias) / periodo if ganancias else 0.0001
    avg_loss = sum(perdidas) / periodo if perdidas else 0.0001

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analizar_activo(symbol):
    init_symbol(symbol)
    simular_precio(symbol)

    data = mercado[symbol]
    precios = data["historial"]

    ema20 = calcular_ema(precios, 20)
    ema50 = calcular_ema(precios, 50)
    rsi = calcular_rsi(precios)

    tendencia = ema20 > ema50
    momentum = rsi > 60
    limpio = 50 < rsi < 70

    score = 0
    if tendencia: score += 1
    if momentum: score += 1
    if limpio: score += 1

    probabilidad = score / 3

    return {
        "symbol": symbol,
        "score": score,
        "probabilidad": probabilidad,
        "precio": data["precio"],
        "rsi": rsi
    }