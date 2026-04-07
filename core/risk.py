import portfolio
import config

def calcular_size(precio, score, prob):

    capital = portfolio.capital

    # =========================
    # BASE
    # =========================
    riesgo_base = config.RIESGO_POR_TRADE

    # =========================
    # CONVICCIÓN (🔥 CLAVE)
    # =========================
    factor = 1

    # ALTA CONFIANZA
    if score >= 2 and prob > 0.6:
        factor = 2   # 🔥 doble inversión

    # MEDIA
    elif score >= 1 and prob > 0.55:
        factor = 1

    # BAJA
    else:
        factor = 0.5  # menos inversión

    # =========================
    # RIESGO FINAL
    # =========================
    riesgo = riesgo_base * factor

    # límite de seguridad
    riesgo = min(riesgo, config.MAX_RIESGO)

    size = (capital * riesgo) / precio

    return size