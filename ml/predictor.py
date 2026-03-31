import pandas as pd
from ml.model import cargar_modelo

model = cargar_modelo()

def predecir(df):

    try:
        last = df.iloc[-1]

        X = pd.DataFrame([[
            last["ema20"],
            last["ema50"],
            last["rsi"],
            last["volume"],
            last["return"],
            last["volatility"],
            last["momentum"]
        ]], columns=[
            "ema20","ema50","rsi","volume",
            "return","volatility","momentum"
        ])

        prob = model.predict_proba(X)[0][1]

        return prob

    except Exception as e:
        print(f"Error ML: {e}")
        return 0.5