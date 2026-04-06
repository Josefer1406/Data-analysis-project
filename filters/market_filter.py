from data.exchange import obtener_datos
from ta.trend import EMAIndicator

def mercado_favorable():
    try:
        df = obtener_datos("BTC/USDT")

        # 🔥 VALIDACIÓN CRÍTICA
        if df is None or len(df) < 210:
            print("⚠️ Datos insuficientes para filtro mercado")
            return False

        df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
        df["ema200"] = EMAIndicator(df["close"], 200).ema_indicator()

        df = df.dropna()

        # 🔥 VALIDACIÓN DESPUÉS DE DROPNA
        if df.empty:
            print("⚠️ DataFrame vacío tras indicadores")
            return False

        last = df.iloc[-1]

        return last["ema50"] > last["ema200"]

    except Exception as e:
        print(f"Error filtro mercado: {e}")
        return False