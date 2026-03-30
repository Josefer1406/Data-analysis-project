import ccxt
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# =========================
# CONFIG
# =========================
CAPITAL_INICIAL = 1000
TIMEFRAME = "5m"
SYMBOL = "BTC/USDT"

exchange = ccxt.okx({
    "enableRateLimit": True
})

# =========================
# DATA
# =========================
def get_data():
    ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=1000)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    return df


# =========================
# BACKTEST PARAMETRICO
# =========================
def backtest(df, ema_fast, ema_slow, rsi_low, rsi_high):

    capital = CAPITAL_INICIAL
    posicion = None

    df["ema_fast"] = EMAIndicator(df["close"], window=ema_fast).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=ema_slow).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    for i in range(ema_slow, len(df)):

        row = df.iloc[i]
        precio = row["close"]

        # entrada
        if posicion is None:

            if row["ema_fast"] > row["ema_slow"] and rsi_low < row["rsi"] < rsi_high:

                size = (capital * 0.05) / precio

                posicion = {
                    "precio": precio,
                    "size": size
                }

        # salida
        else:
            pnl = (precio - posicion["precio"]) / posicion["precio"]

            if pnl >= 0.04 or pnl <= -0.02:

                capital += (precio - posicion["precio"]) * posicion["size"]
                posicion = None

    return capital


# =========================
# OPTIMIZADOR
# =========================
def optimize():

    df = get_data()

    best_result = 0
    best_params = None

    print("🔎 Iniciando optimización...\n")

    for ema_fast in [10, 15, 20]:
        for ema_slow in [40, 50, 60]:
            for rsi_low in [30, 35, 40]:
                for rsi_high in [60, 65, 70]:

                    if ema_fast >= ema_slow:
                        continue

                    capital_final = backtest(
                        df.copy(),
                        ema_fast,
                        ema_slow,
                        rsi_low,
                        rsi_high
                    )

                    print(f"EMA {ema_fast}/{ema_slow} | RSI {rsi_low}-{rsi_high} → {capital_final:.2f}")

                    if capital_final > best_result:
                        best_result = capital_final
                        best_params = (ema_fast, ema_slow, rsi_low, rsi_high)

    print("\n🏆 ===== MEJOR CONFIGURACIÓN =====")
    print(f"EMA FAST: {best_params[0]}")
    print(f"EMA SLOW: {best_params[1]}")
    print(f"RSI LOW: {best_params[2]}")
    print(f"RSI HIGH: {best_params[3]}")
    print(f"Capital final: {best_result:.2f}")
    print("=================================\n")


if __name__ == "__main__":
    optimize()