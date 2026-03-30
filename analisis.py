import pandas as pd

archivo = "trades_log.csv"

df = pd.read_csv(archivo, header=None)

# Detectar número de columnas automáticamente
num_cols = len(df.columns)

if num_cols == 6:
    df.columns = ["fecha", "symbol", "tipo", "precio", "size", "pnl"]

elif num_cols == 5:
    df.columns = ["fecha", "symbol", "tipo", "precio", "size"]
    df["pnl"] = 0  # crear columna vacía

else:
    print("❌ Formato de CSV desconocido")
    exit()

# Filtrar ventas (solo ellas tienen pnl real)
ventas = df[df["tipo"] == "SELL"]

total_trades = len(ventas)
ganadoras = len(ventas[ventas["pnl"] > 0])
perdedoras = len(ventas[ventas["pnl"] <= 0])

win_rate = (ganadoras / total_trades) * 100 if total_trades > 0 else 0

pnl_total = ventas["pnl"].sum()

promedio_ganancia = ventas[ventas["pnl"] > 0]["pnl"].mean()
promedio_perdida = ventas[ventas["pnl"] <= 0]["pnl"].mean()

print("\n📊 ===== ANALISIS DEL BOT =====")
print(f"Trades totales: {total_trades}")
print(f"Ganadoras: {ganadoras}")
print(f"Perdedoras: {perdedoras}")
print(f"Win Rate: {win_rate:.2f}%")
print(f"PnL Total: {pnl_total:.2f} USDT")
print(f"Ganancia promedio: {promedio_ganancia}")
print(f"Pérdida promedio: {promedio_perdida}")
print("================================\n")