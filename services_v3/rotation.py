import config


# =========================
# ROTACIÓN INSTITUCIONAL
# =========================
def evaluar_rotacion(portfolio, candidatos):

    if not portfolio.posiciones:
        return None

    if not candidatos:
        return None

    mejor = candidatos[0]

    peor_symbol = None
    peor_score = 999

    for s, pos in portfolio.posiciones.items():

        score = pos.get("score", 0)

        if score < peor_score:
            peor_score = score
            peor_symbol = s

    if peor_symbol is None:
        return None

    # =========================
    # CONDICIÓN DE ROTACIÓN
    # =========================
    if mejor["score"] > peor_score * (1 + config.ROTACION_UMBRAL):

        return {
            "salir": peor_symbol,
            "entrar": mejor
        }

    return None