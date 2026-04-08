import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("🚀 BOT CUANT INSTITUCIONAL PRO")

# =========================
# Obtener datos del bot
# =========================

try:
    data = requests.get("http://localhost:8080/data").json()
except:
    st.error("No se pudo conectar con el bot")
    st.stop()

capital = data.get("capital", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

# =========================
# KPIs PRINCIPALES
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("💰 Capital", f"${round(capital,2)}")
col2.metric("📊 Posiciones", len(posiciones))
col3.metric("📈 Trades", len(historial))

# =========================
# POSICIONES ACTIVAS
# =========================

st.subheader("📊 Posiciones activas")

if posiciones:
    df = pd.DataFrame(posiciones).T
    st.dataframe(df)
else:
    st.info("No hay posiciones abiertas")

# =========================
# HISTORIAL
# =========================

st.subheader("📜 Historial de operaciones")

if historial:
    df_hist = pd.DataFrame(historial)
    st.dataframe(df_hist)
else:
    st.info("Sin operaciones aún")

# =========================
# EQUITY CURVE
# =========================

st.subheader("📈 Evolución del capital")

if historial:
    equity = []
    capital_temp = 1000

    for trade in historial:
        capital_temp *= (1 + trade["pnl"])
        equity.append(capital_temp)

    st.line_chart(equity)
else:
    st.info("No hay datos suficientes")