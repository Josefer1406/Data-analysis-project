import csv
import os
import time

ARCHIVO = "trades_log.csv"

def inicializar_log():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "fecha",
                "symbol",
                "tipo",
                "precio",
                "size",
                "pnl",
                "capital"
            ])

def log_trade(symbol, tipo, precio, size, pnl, capital):
    with open(ARCHIVO, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            tipo,
            precio,
            size,
            pnl,
            capital
        ])