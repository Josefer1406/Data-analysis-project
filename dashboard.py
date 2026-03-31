import pandas as pd
import streamlit as st

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")

st.title("📊 Dashboard Bot Trading")

archivo = "trades_log.csv"

try:
    df = pd.read_csv(archivo, header=None)

    # =========================
    # DETECTAR FORMATO CSV
    # =========================
    if len(df.columns) == 7:
        df.columns = ["fecha","symbol","tipo","precio","size","pnl","capital"]

    elif len(df.columns) == 6:
        df.columns = ["fecha","symbol","tipo","precio","size","pnl"]
        df["capital"] = df["pnl"].cumsum()

    elif len(df.columns) == 5:
        df.columns = ["fecha","symbol","tipo","precio","size"]
        df["pnl"] = 0
        df["capital"] = 0

    else:
        st.error("❌ Formato de CSV no reconocido")
        st.stop()

    # =========================
    # LIMPIEZA DE DATOS
    # =========================
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # solo ventas tienen pnl real
    ventas = df[df["tipo"] == "SELL"].copy()

    # =========================
    # MÉTRICAS
    # =========================
    st.subheader("📈 Métricas")

    col1, col2, col3 = st.columns(3)

    pnl_total = ventas["pnl"].sum()
    total_trades = len(ventas)

    win_rate = (
        len(ventas[ventas["pnl"] > 0]) / total_trades * 100
        if total_trades > 0 else 0
    )

    col1.metric("PnL Total", f"{pnl_total:.2f} USDT")
    col2.metric("Trades cerrados", total_trades)
    col3.metric("Win Rate", f"{win_rate:.2f}%")

    # =========================
    # CAPITAL ACTUAL
    # =========================
    st.subheader("💰 Estado del capital")

    if not df.empty:
        capital_actual = df["capital"].iloc[-1]
        capital_inicial = df["capital"].iloc[0]

        col4, col5 = st.columns(2)

        col4.metric("Capital inicial", f"{capital_inicial:.2f} USDT")
        col5.metric("Capital actual", f"{capital_actual:.2f} USDT")

    # =========================
    # EQUITY CURVE
    # =========================
    st.subheader("📊 Curva de capital")

    if not ventas.empty:
        if "capital" in ventas.columns:
            st.line_chart(ventas.set_index("fecha")["capital"])
        else:
            ventas["capital"] = ventas["pnl"].cumsum()
            st.line_chart(ventas.set_index("fecha")["capital"])
    else:
        st.warning("⚠️ No hay trades cerrados aún")

    # =========================
    # HISTORIAL
    # =========================
    st.subheader("📋 Historial de trades")

    st.dataframe(ventas)

except Exception as e:
    st.error(f"❌ No se pudo cargar el archivo: {e}")