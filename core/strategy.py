from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import config

def aplicar_estrategia(df):

    df["ema_fast"] = EMAIndicator(
        df["close"],
        window=config.EMA_FAST
    ).ema_indicator()

    df["ema_slow"] = EMAIndicator(
        df["close"],
        window=config.EMA_SLOW
    ).ema_indicator()

    df["rsi"] = RSIIndicator(
        df["close"],
        window=14
    ).rsi()

    return df


def evaluar(df):

    row = df.iloc[-1]

    if row["ema_fast"] > row["ema_slow"] and row["rsi"] < config.RSI_BUY:
        return "BUY"

    if row["rsi"] > config.RSI_SELL:
        return "SELL"

    return "HOLD"