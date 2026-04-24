import numpy as np


def calcular_score(features, ml_prob=0.5):

    m5 = features["momentum_5"]
    m15 = features["momentum_15"]
    m1h = features["momentum_1h"]

    trend = features["trend"]
    vol_ratio = min(features["vol_ratio"], 3) / 3
    volatility = features["volatility"]

    # =========================
    # 🔥 FILTRO DE CALIDAD REAL
    # =========================
    if m5 < 0 or m15 < 0:
        return 0  # evita basura total

    # =========================
    # 🔥 SCORE DE MOMENTUM REAL
    # =========================
    momentum_score = (
        (m5 * 0.4) +
        (m15 * 0.35) +
        (m1h * 0.25)
    )

    # =========================
    # 🔥 PENALIZACIÓN POR VOLATILIDAD MALA
    # =========================
    if volatility > 0.04:
        momentum_score *= 0.7

    # =========================
    # 🔥 BONUS POR TENDENCIA
    # =========================
    if trend > 0:
        momentum_score *= 1.2

    # =========================
    # 🔥 ML COMO CONFIRMACIÓN
    # =========================
    score = (momentum_score * 0.75) + (ml_prob * 0.25)

    return float(score)