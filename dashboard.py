import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Bot Trading PRO")

archivo = "trades_log.csv"

try:
    df = pd.read_csv(archivo)

    # =========================
    # LIMPIEZA
    # =========================
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # solo ventas para métricas reales
    ventas = df[df["tipo"] == "SELL"].copy()

    # =========================
    # MÉTRICAS
    # =========================
    st.subheader("📈 Métricas generales")

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
    # CAPITAL
    # =========================
    st.subheader("💰 Capital")

    if not df.empty:
        capital_inicial = df["capital"].iloc[0]
        capital_actual = df["capital"].iloc[-1]

        col4, col5 = st.columns(2)

        col4.metric("Capital inicial", f"{capital_inicial:.2f} USDT")
        col5.metric("Capital actual", f"{capital_actual:.2f} USDT")

    # =========================
    # CURVA DE CAPITAL
    # =========================
    st.subheader("📊 Curva de capital")

    if "capital" in df.columns:
        df_capital = df.copy()
        df_capital = df_capital.dropna(subset=["fecha"])
        df_capital = df_capital.set_index("fecha")

        st.line_chart(df_capital["capital"])

    # =========================
    # HISTORIAL
    # =========================
    st.subheader("📋 Historial de trades")

    st.dataframe(df)

except Exception as e:
    st.error(f"❌ Error cargando archivo: {e}")