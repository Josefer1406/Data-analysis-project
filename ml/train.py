import ccxt
import pandas as pd

from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

from sklearn.ensemble import RandomForestClassifier

from ml.model import guardar_modelo

# =========================
# CONFIG
# =========================
SYMBOL = "BTC/USDT"
TIMEFRAME = "5m"
LIMIT = 1000

exchange = ccxt.okx({
    "enableRateLimit": True
})

# =========================
# DESCARGAR DATOS
# =========================
def get_data():

    ohlcv = exchange.fetch_ohlcv(
        SYMBOL,
        timeframe=TIMEFRAME,
        limit=LIMIT
    )

    df = pd.DataFrame(
        ohlcv,
        columns=["time","open","high","low","close","volume"]
    )

    return df


# =========================
# PREPARAR DATOS
# =========================
def preparar_datos(df):

    # indicadores
    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

    # target: si sube en próximas velas
    df["target"] = (df["close"].shift(-3) > df["close"]).astype(int)

    # eliminar NaN
    df = df.dropna()

    # features
    X = df[["ema20","ema50","rsi","volume"]]

    # etiqueta
    y = df["target"]

    return X, y


# =========================
# ENTRENAR MODELO
# =========================
def entrenar_modelo():

    print("📊 Descargando datos...")
    df = get_data()

    print("🧠 Preparando datos...")
    X, y = preparar_datos(df)

    print("🤖 Entrenando modelo...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )

    model.fit(X, y)

    guardar_modelo(model)

    print("✅ Modelo entrenado correctamente")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    entrenar_modelo()