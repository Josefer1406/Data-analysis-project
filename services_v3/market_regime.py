import numpy as np


# =========================
# DETECCIÓN DE MERCADO REAL
# =========================
def detectar_regimen(features_list):

    if not features_list:
        return "neutral"

    momentum = [f["momentum_1h"] for f in features_list]
    volatility = [f["volatility"] for f in features_list]

    avg_momentum = np.mean(momentum)
    avg_vol = np.mean(volatility)

    # =========================
    # LÓGICA REAL
    # =========================
    if avg_momentum > 0.01 and avg_vol < 0.03:
        return "bull"

    if avg_momentum < -0.01:
        return "bear"

    return "lateral"