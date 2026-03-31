import joblib
import os

MODEL_PATH = "ml_model.pkl"


def guardar_modelo(model):
    try:
        joblib.dump(model, MODEL_PATH)
        print("💾 Modelo guardado correctamente")
    except Exception as e:
        print(f"Error guardando modelo: {e}")


def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "❌ No existe el modelo. Ejecuta primero: python ml/train.py"
        )

    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        raise RuntimeError(f"Error cargando modelo: {e}")