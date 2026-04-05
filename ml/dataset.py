import pandas as pd
from database import conectar

def cargar_datos():

    conn = conectar()

    query = """
        SELECT fecha, symbol, precio, pnl, capital
        FROM trades
        ORDER BY fecha ASC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def crear_features(df):

    # =========================
    # RETORNOS
    # =========================
    df["retorno"] = df["precio"].pct_change()

    # =========================
    # VOLATILIDAD
    # =========================
    df["volatilidad"] = df["retorno"].rolling(5).std()

    # =========================
    # MOMENTUM
    # =========================
    df["momentum"] = df["precio"].pct_change(3)

    # =========================
    # TARGET (GANANCIA)
    # =========================
    df["target"] = (df["pnl"] > 0).astype(int)

    df = df.dropna()

    return df