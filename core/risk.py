import portfolio
import config

def calcular_size(precio, score, prob):

    capital = portfolio.capital

    # =========================
    # PESO POR PROBABILIDAD
    # =========================
    # normalizar entre 0 y 1
    prob = max(0.4, min(prob, 0.9))

    peso_prob = (prob - 0.4) / (0.9 - 0.4)

    # =========================
    # PESO POR SCORE
    # =========================
    peso_score = score / 3  # max score esperado = 3

    # =========================
    # CONVICCIÓN FINAL
    # =========================
    conviccion = (peso_prob * 0.7) + (peso_score * 0.3)

    # =========================
    # RIESGO DINÁMICO
    # =========================
    riesgo = config.RIESGO_POR_TRADE * (0.5 + conviccion)

    # límite institucional
    riesgo = min(riesgo, config.MAX_RIESGO)

    # =========================
    # SIZE FINAL
    # =========================
    capital_asignado = capital * riesgo

    size = capital_asignado / precio

    return size