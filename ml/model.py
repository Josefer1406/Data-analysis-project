import joblib
import os

PATH = "ml/model.pkl"

def guardar(model):
    os.makedirs("ml", exist_ok=True)
    joblib.dump(model, PATH)

def cargar():
    if os.path.exists(PATH):
        return joblib.load(PATH)
    return None