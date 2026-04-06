import numpy as np
from ml.model import cargar

model = cargar()

def predecir(f):
    global model
    if model is None:
        return 0.5

    X = np.array([[f["ema20"], f["ema50"], f["rsi"], f["volumen"], f["volatilidad"]]])
    return model.predict_proba(X)[0][1]