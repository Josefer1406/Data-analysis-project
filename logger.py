import csv
import time

ARCHIVO = "trades_log.csv"

def log_trade(symbol, tipo, precio, cantidad, pnl):

    with open(ARCHIVO, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            tipo,
            precio,
            cantidad,
            pnl
        ])