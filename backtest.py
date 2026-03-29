import ccxt
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from config import SYMBOLS, TIMEFRAME, CAPITAL_INICIAL

exchange = ccxt.binance()

capital = CAPITAL_INICIAL
position = 0
precio_entrada = 0

def get_historical_data(symbol):
    print(f"Descargando datos de {symbol}...")
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=500)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    return df


def run_backtest(symbol):

    global capital, position, precio_entrada

    df = get_historical_data(symbol)

    trades = 0

    for i in range(50, len(df)):

        row = df.iloc[i]

        precio = row["close"]
        ema20 = row["ema20"]
        ema50 = row["ema50"]
        rsi = row["rsi"]

        # COMPRA
        if ema20 > ema50 and rsi < 35 and position == 0:
            monto = capital * 0.1
            position = monto / precio
            capital -= monto
            precio_entrada = precio
            trades += 1

        # VENTA
        elif position > 0:
            ganancia = (precio - precio_entrada) / precio_entrada

            if rsi > 65 or ganancia >= 0.03 or ganancia <= -0.02:
                capital += position * precio
                position = 0

    print("\n===== RESULTADO BACKTEST =====")
    print(f"Capital final: {capital:.2f} USDT")
    print(f"Trades realizados: {trades}")
    print(f"Ganancia total: {(capital/CAPITAL_INICIAL-1)*100:.2f}%")
    print("==============================\n")


if __name__ == "__main__":

    for symbol in SYMBOLS:
        run_backtest(symbol)