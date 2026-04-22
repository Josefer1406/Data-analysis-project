def evaluar_rotacion(portfolio, candidatos, mercado):

    if not portfolio.posiciones or not candidatos:
        return None

    mejor = candidatos[0]

    peor_symbol = None
    peor_score = 999

    for s, pos in portfolio.posiciones.items():
        if pos["score"] < peor_score:
            peor_score = pos["score"]
            peor_symbol = s

    if peor_symbol is None:
        return None

    # 🔥 ROTAR SOLO SI VALE LA PENA
    mejora = mejor["score"] - peor_score

    if mercado == "bull":
        umbral = 0.06
    elif mercado == "lateral":
        umbral = 0.04
    else:
        umbral = 0.03

    if mejora > umbral:
        return {
            "salir": peor_symbol,
            "entrar": mejor
        }

    return None