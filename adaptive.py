import pandas as pd

def evaluar_rendimiento():

    try:
        df = pd.read_csv("trades_log.csv", header=None)

        if len(df.columns) < 6:
            return "NEUTRO"

        df.columns = ["fecha","symbol","tipo","precio","size","pnl"]

        ventas = df[df["tipo"] == "SELL"].tail(20)

        if len(ventas) < 5:
            return "NEUTRO"

        pnl_total = ventas["pnl"].sum()

        if pnl_total > 0:
            return "GANANDO"
        else:
            return "PERDIENDO"

    except:
        return "NEUTRO"


def ajustar_parametros():

    estado = evaluar_rendimiento()

    if estado == "GANANDO":
        print("📈 Bot en racha positiva → modo agresivo")

        return {
            "MIN_SCORE": 2,
            "RIESGO": 0.05
        }

    elif estado == "PERDIENDO":
        print("📉 Bot en pérdida → modo defensivo")

        return {
            "MIN_SCORE": 4,
            "RIESGO": 0.02
        }

    else:
        print("⚖️ Modo neutral")

        return {
            "MIN_SCORE": 3,
            "RIESGO": 0.03
        }