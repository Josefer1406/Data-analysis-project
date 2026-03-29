import csv
import config
from datetime import datetime

def guardar_trade(symbol, side, price, size):

    with open(config.LOG_FILE, "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now(),
            symbol,
            side,
            price,
            size
        ])