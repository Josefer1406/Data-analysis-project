import pandas as pd

def calcular_indicadores(data):

    df = pd.DataFrame(
        data,
        columns=["time","open","high","low","close","volume"]
    )

    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()

    return df


def generar_senal(df):

    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
        return "BUY"

    if df["EMA20"].iloc[-1] < df["EMA50"].iloc[-1]:
        return "SELL"

    return "HOLD"