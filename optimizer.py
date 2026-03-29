import ccxt
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from config import SYMBOLS, TIMEFRAME, CAPITAL_INICIAL

exchange = ccxt.binance()

def get_data(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=500)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    return df


def run_strategy(df, ema_fast, ema_slow, rsi_buy, rsi_sell):

    capital = CAPITAL_INICIAL
    position = 0
    precio_entrada = 0

    df["ema_fast"] = EMAIndicator(df["close"], window=ema_fast).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=ema_slow).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    for i in range(50, len(df)):

        row = df.iloc[i]

        precio = row["close"]

        # COMPRA
        if (
            row["ema_fast"] > row["ema_slow"]
            and row["rsi"] < rsi_buy
            and position == 0
        ):
            monto = capital * 0.1
            position = monto / precio
            capital -= monto
            precio_entrada = precio

        # VENTA
        elif position > 0:

            ganancia = (precio - precio_entrada) / precio_entrada

            if row["rsi"] > rsi_sell or ganancia >= 0.03 or ganancia <= -0.02:
                capital += position * precio
                position = 0

    return capital


def optimize(symbol):

    print(f"\n🔎 Optimizando {symbol}")

    df = get_data(symbol)

    mejor_resultado = 0
    mejor_config = None

    for ema_fast in [10, 15, 20]:
        for ema_slow in [40, 50, 60]:
            for rsi_buy in [30, 35, 40]:
                for rsi_sell in [60, 65, 70]:

                    if ema_fast >= ema_slow:
                        continue

                    capital_final = run_strategy(
                        df.copy(),
                        ema_fast,
                        ema_slow,
                        rsi_buy,
                        rsi_sell,
                    )

                    if capital_final > mejor_resultado:
                        mejor_resultado = capital_final
                        mejor_config = (
                            ema_fast,
                            ema_slow,
                            rsi_buy,
                            rsi_sell,
                        )

    print("✅ Mejor configuración encontrada:")
    print(f"EMA FAST: {mejor_config[0]}")
    print(f"EMA SLOW: {mejor_config[1]}")
    print(f"RSI BUY: {mejor_config[2]}")
    print(f"RSI SELL: {mejor_config[3]}")
    print(f"Capital final: {mejor_resultado:.2f}")


if __name__ == "__main__":

    for symbol in SYMBOLS:
        optimize(symbol)