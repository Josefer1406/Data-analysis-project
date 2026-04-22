import numpy as np


# =========================
# NORMALIZACIÓN
# =========================
def normalizar(x, min_val=-0.05, max_val=0.05):

    if x is None:
        return 0

    x = max(min(x, max_val), min_val)

    return (x - min_val) / (max_val - min_val)


# =========================
# SCORE CUANT REAL
# =========================
def calcular_score(features, ml_prob=0.5):

    m5 = normalizar(features["momentum_5"])
    m15 = normalizar(features["momentum_15"])
    m1h = normalizar(features["momentum_1h"])

    trend = normalizar(features["trend"])
    vol_ratio = min(features["vol_ratio"], 3) / 3
    volatility = 1 - min(features["volatility"], 0.05) / 0.05

    # =========================
    # COMBINACIÓN INSTITUCIONAL
    # =========================
    score = (
        0.25 * m5 +
        0.25 * m15 +
        0.20 * m1h +
        0.10 * trend +
        0.10 * vol_ratio +
        0.10 * volatility
    )

    # ajuste por ML
    score = (score * 0.7) + (ml_prob * 0.3)

    return float(score)