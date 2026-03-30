import pandas as pd

def calcular_min_score():

    try:
        df = pd.read_csv("trades_log.csv", header=None)

        if len(df.columns) < 6:
            return 3

        df.columns = ["fecha","symbol","tipo","precio","size","pnl"]

        ventas = df[df["tipo"] == "SELL"].tail(20)

        if len(ventas) < 5:
            return 3

        pnl_total = ventas["pnl"].sum()

        # Ajuste dinámico
        if pnl_total > 0:
            print("📈 Bot ganando → más agresivo")
            return 2
        else:
            print("📉 Bot perdiendo → más conservador")
            return 4

    except:
        return 3