import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from ml.model import guardar_modelo
from ml.dataset import cargar_datos, crear_features

def entrenar():

    df = cargar_datos()

    if len(df) < 50:
        print("❌ No hay suficientes datos para entrenar")
        return

    df = crear_features(df)

    # =========================
    # FEATURES
    # =========================
    X = df[[
        "retorno",
        "volatilidad",
        "momentum"
    ]]

    y = df["target"]

    # =========================
    # SPLIT
    # =========================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # =========================
    # MODELO
    # =========================
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    # =========================
    # EVALUACIÓN
    # =========================
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"📊 Accuracy: {acc:.2f}")

    guardar_modelo(model)

    print("✅ Modelo actualizado con datos reales")