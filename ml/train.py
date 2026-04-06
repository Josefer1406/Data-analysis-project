import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from ml.model import guardar
from database import conectar

def entrenar():
    conn = conectar()

    df = pd.read_sql("""
        SELECT f.*, t.pnl
        FROM features f
        JOIN trades t ON f.fecha = t.fecha AND f.symbol = t.symbol
    """, conn)

    conn.close()

    if len(df) < 100:
        print("No hay suficientes datos")
        return

    df["target"] = (df["pnl"] > 0).astype(int)

    X = df[["ema20","ema50","rsi","volumen","volatilidad"]]
    y = df["target"]

    model = RandomForestClassifier(n_estimators=200, max_depth=6)
    model.fit(X, y)

    guardar(model)
    print("Modelo entrenado con datos reales")