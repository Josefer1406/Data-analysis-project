from ml.model import cargar_modelo
import numpy as np

model = cargar_modelo()

def predecir(features_dict):

    global model

    if model is None:
        return 0.5  # neutral

    X = np.array([[
        features_dict["ema20"],
        features_dict["ema50"],
        features_dict["rsi"],
        features_dict["volumen"],
        features_dict["volatilidad"]
    ]])

    prob = model.predict_proba(X)[0][1]

    return prob