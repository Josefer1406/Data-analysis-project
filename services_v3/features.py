import numpy as np


# =========================
# FEATURES CUANT REALES
# =========================
def calcular_features(data):

    df5 = data["5m"]
    df15 = data["15m"]
    df1h = data["1h"]

    # =========================
    # RETURNS
    # =========================
    df5["returns"] = df5["close"].pct_change()
    df15["returns"] = df15["close"].pct_change()
    df1h["returns"] = df1h["close"].pct_change()

    # =========================
    # MOMENTUM MULTI-TF
    # =========================
    momentum_5 = df5["close"].iloc[-1] / df5["close"].iloc[-5] - 1
    momentum_15 = df15["close"].iloc[-1] / df15["close"].iloc[-5] - 1
    momentum_1h = df1h["close"].iloc[-1] / df1h["close"].iloc[-5] - 1

    # =========================
    # TENDENCIA
    # =========================
    ema20 = df5["close"].ewm(span=20).mean().iloc[-1]
    ema50 = df5["close"].ewm(span=50).mean().iloc[-1]

    trend = (ema20 / ema50) - 1

    # =========================
    # VOLUMEN RELATIVO
    # =========================
    vol_actual = df5["volume"].iloc[-1]
    vol_media = df5["volume"].rolling(20).mean().iloc[-1]

    vol_ratio = vol_actual / vol_media if vol_media > 0 else 0

    # =========================
    # VOLATILIDAD
    # =========================
    volatility = df5["returns"].std()

    # =========================
    # CONSOLIDAR
    # =========================
    features = {
        "momentum_5": float(momentum_5),
        "momentum_15": float(momentum_15),
        "momentum_1h": float(momentum_1h),
        "trend": float(trend),
        "vol_ratio": float(vol_ratio),
        "volatility": float(volatility)
    }

    return features