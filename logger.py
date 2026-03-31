import csv
import time
import portfolio


def log_trade(symbol, tipo, precio, size, pnl):

    capital_actual = float(portfolio.capital)

    with open("trades_log.csv", "a", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            tipo,
            precio,
            size,
            pnl,
            capital_actual
        ])