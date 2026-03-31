import ccxt
import pandas as pd
import numpy as np

from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from ml.model import guardar_modelo

# =========================
# CONFIG
# =========================
SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT"
]

TIMEFRAME = "5m"
LIMIT = 1000

exchange = ccxt.okx({"enableRateLimit": True})

# =========================
# DESCARGAR DATA MULTI-CRYPTO
# =========================
def get_data():

    dfs = []

    for symbol in SYMBOLS:
        print(f"Descargando {symbol}...")

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)

        df = pd.DataFrame(
            ohlcv,
            columns=["time","open","high","low","close","volume"]
        )

        df["symbol"] = symbol

        dfs.append(df)

    return pd.concat(dfs)


# =========================
# FEATURES AVANZADAS
# =========================
def crear_features(df):

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    # retornos
    df["return"] = df["close"].pct_change()

    # volatilidad
    df["volatility"] = df["return"].rolling(10).std()

    # momentum real
    df["momentum"] = df["close"] - df["close"].shift(5)

    # target (sube en próximas velas)
    df["target"] = (df["close"].shift(-3) > df["close"]).astype(int)

    df = df.dropna()

    features = [
        "ema20",
        "ema50",
        "rsi",
        "volume",
        "return",
        "volatility",
        "momentum"
    ]

    X = df[features]
    y = df["target"]

    return X, y


# =========================
# ENTRENAMIENTO PROFESIONAL
# =========================
def train():

    print("📊 Descargando datos multi-crypto...")
    df = get_data()

    print("🧠 Creando features avanzadas...")
    X, y = crear_features(df)

    print("📊 Dividiendo dataset (train/test)...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        shuffle=False  # importante en series temporales
    )

    print("🤖 Entrenando modelo...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )

    model.fit(X_train, y_train)

    # evaluación real
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print(f"\n📊 Accuracy real (test): {acc:.2f}")

    guardar_modelo(model)

    print("✅ Modelo entrenado correctamente")


if __name__ == "__main__":
    train()