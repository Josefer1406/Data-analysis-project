import pandas as pd
import streamlit as st
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Dashboard Trading Profesional (Hedge Fund)")

# 🔥 API DE TU BOT (CAMBIA ESTO)
url = "https://data-analysis-project-production.up.railway.app/data"

# =========================
# CARGAR DATOS
# =========================
try:
    df = pd.read_json(url)

    if df.empty:
        st.warning("No hay datos aún")
        st.stop()

    df["fecha"] = pd.to_datetime(df["fecha"])

    # =========================
    # EQUITY CURVE
    # =========================
    df = df.sort_values("fecha")

    capital_series = df["capital"]

    # =========================
    # RETORNOS
    # =========================
    returns = capital_series.pct_change().dropna()

    # =========================
    # MÉTRICAS
    # =========================
    ventas = df[df["tipo"] == "SELL"]

    pnl_total = ventas["pnl"].sum()
    total_trades = len(ventas)

    win_rate = (
        len(ventas[ventas["pnl"] > 0]) / total_trades * 100
        if total_trades > 0 else 0
    )

    capital_inicial = df["capital"].iloc[0]
    capital_actual = df["capital"].iloc[-1]

    # =========================
    # DRAWDOWN
    # =========================
    rolling_max = capital_series.cummax()
    drawdown = (capital_series - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # =========================
    # SHARPE RATIO
    # =========================
    sharpe = (
        (returns.mean() / returns.std()) * np.sqrt(252)
        if returns.std() != 0 else 0
    )

    # =========================
    # MÉTRICAS UI
    # =========================
    st.subheader("📈 Métricas clave")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("PnL Total", f"{pnl_total:.2f} USDT")
    col2.metric("Win Rate", f"{win_rate:.2f}%")
    col3.metric("Max Drawdown", f"{max_drawdown:.2%}")
    col4.metric("Sharpe Ratio", f"{sharpe:.2f}")

    col5, col6 = st.columns(2)

    col5.metric("Capital inicial", f"{capital_inicial:.2f}")
    col6.metric("Capital actual", f"{capital_actual:.2f}")

    # =========================
    # GRÁFICAS
    # =========================
    st.subheader("📊 Curva de capital")
    st.line_chart(capital_series)

    st.subheader("📉 Drawdown")
    st.area_chart(drawdown)

    # =========================
    # HISTORIAL
    # =========================
    st.subheader("📋 Historial de operaciones")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error cargando datos: {e}")