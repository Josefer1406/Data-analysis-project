import joblib
import os

MODEL_PATH = "ml_model.pkl"


def guardar_modelo(model):
    joblib.dump(model, MODEL_PATH)
    print("💾 Modelo guardado correctamente")


def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ No existe el modelo. Ejecuta train.py primero.")

    model = joblib.load(MODEL_PATH)
    return model