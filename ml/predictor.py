import pandas as pd
from ml.model import cargar_modelo

# cargar modelo una sola vez
model = cargar_modelo()

def predecir(df):

    try:
        last = df.iloc[-1]

        # construir features
        X = pd.DataFrame([[
            last["ema20"],
            last["ema50"],
            last["rsi"],
            last["volume"]
        ]], columns=["ema20","ema50","rsi","volume"])

        # probabilidad de subida
        prob = model.predict_proba(X)[0][1]

        return prob

    except Exception as e:
        print(f"Error en predicción ML: {e}")
        return 0.5  # neutral