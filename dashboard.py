import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 QUANT DASHBOARD PRO")

url = "https://data-analysis-project-production.up.railway.app/data"

try:
    df = pd.read_json(url)

    # =========================
    # VALIDACIÓN
    # =========================
    if df is None or df.empty:
        st.warning("⚠️ No hay datos aún del bot")
        st.stop()

    columnas_esperadas = ["fecha", "symbol", "tipo", "precio", "size", "pnl", "capital"]

    for col in columnas_esperadas:
        if col not in df.columns:
            st.error(f"❌ Falta columna: {col}")
            st.write("Columnas recibidas:", df.columns)
            st.stop()

    # =========================
    # PROCESAMIENTO
    # =========================
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.sort_values("fecha")

    capital = df["capital"]

    if len(capital) < 2:
        st.warning("⚠️ Aún no hay suficientes datos para métricas")
        st.dataframe(df)
        st.stop()

    returns = capital.pct_change().dropna()

    ventas = df[df["tipo"] == "SELL"]

    pnl = ventas["pnl"].sum()

    winrate = (
        len(ventas[ventas["pnl"] > 0]) / len(ventas)
        if len(ventas) > 0 else 0
    )

    # =========================
    # DRAWDOWN
    # =========================
    roll = capital.cummax()
    dd = (capital - roll) / roll

    # =========================
    # SHARPE (CORREGIDO)
    # =========================
    sharpe = (
        (returns.mean() / returns.std()) * np.sqrt(252)
        if returns.std() != 0 else 0
    )

    # =========================
    # MÉTRICAS
    # =========================
    st.subheader("📈 Métricas")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("PnL", round(pnl, 2))
    col2.metric("Win Rate", round(winrate * 100, 2))
    col3.metric("Drawdown %", round(dd.min() * 100, 2))
    col4.metric("Sharpe", round(sharpe, 2))

    # =========================
    # GRÁFICAS
    # =========================
    st.subheader("💰 Curva de capital")
    st.line_chart(capital)

    st.subheader("📉 Drawdown")
    st.area_chart(dd)

    # =========================
    # TABLA
    # =========================
    st.subheader("📋 Historial")
    st.dataframe(df)

except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")