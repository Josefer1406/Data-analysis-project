import ccxt
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

# =========================
# CONFIG
# =========================
CAPITAL_INICIAL = 1000
RIESGO = 0.05
STOP_LOSS = -0.02
TAKE_PROFIT = 0.04
TIMEFRAME = "5m"

SYMBOL = "BTC/USDT"

# =========================
# EXCHANGE
# =========================
exchange = ccxt.okx({
    "enableRateLimit": True
})

# =========================
# DESCARGAR DATOS
# =========================
def get_data():
    ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=1000)

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    return df


# =========================
# BACKTEST
# =========================
def run_backtest():

    capital = CAPITAL_INICIAL
    posicion = None
    trades = []

    df = get_data()

    # indicadores
    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    for i in range(50, len(df)):

        row = df.iloc[i]
        precio = row["close"]

        # =========================
        # ENTRADA
        # =========================
        if posicion is None:

            if row["ema20"] > row["ema50"] and 30 < row["rsi"] < 50:

                size = (capital * RIESGO) / precio

                posicion = {
                    "precio": precio,
                    "size": size
                }

        # =========================
        # SALIDA
        # =========================
        else:

            pnl = (precio - posicion["precio"]) / posicion["precio"]

            if pnl <= STOP_LOSS or pnl >= TAKE_PROFIT:

                ganancia = (precio - posicion["precio"]) * posicion["size"]
                capital += ganancia

                trades.append(ganancia)

                posicion = None

    # =========================
    # RESULTADOS
    # =========================
    total_trades = len(trades)
    pnl_total = sum(trades)

    ganadoras = len([t for t in trades if t > 0])
    perdedoras = len([t for t in trades if t <= 0])

    win_rate = (ganadoras / total_trades) * 100 if total_trades > 0 else 0

    print("\n📊 ===== BACKTEST PROFESIONAL =====")
    print(f"Capital inicial: {CAPITAL_INICIAL}")
    print(f"Capital final: {capital:.2f}")
    print(f"PnL total: {pnl_total:.2f}")
    print(f"Trades: {total_trades}")
    print(f"Win rate: {win_rate:.2f}%")
    print("==================================\n")


if __name__ == "__main__":
    run_backtest()