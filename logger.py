import csv
import time

def log_trade(symbol, tipo, precio, size, pnl):

    with open("trades_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            tipo,
            precio,
            size,
            pnl
        ])