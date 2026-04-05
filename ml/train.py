import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from ml.model import guardar_modelo

def entrenar_modelo(df):

    # =========================
    # FEATURES
    # =========================
    X = df[[
        "ema20",
        "ema50",
        "rsi",
        "volumen",
        "volatilidad"
    ]]

    # =========================
    # TARGET
    # =========================
    y = df["target"]  # 1 sube, 0 baja

    # =========================
    # MODELO BASE
    # =========================
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )

    model.fit(X, y)

    guardar_modelo(model)

    print("✅ Modelo entrenado")