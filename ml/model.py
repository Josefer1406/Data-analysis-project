import joblib
import os

MODEL_PATH = "ml/model.pkl"

def guardar_modelo(modelo):
    os.makedirs("ml", exist_ok=True)
    joblib.dump(modelo, MODEL_PATH)

def cargar_modelo():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None