import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 BOT CUANT PRO")

API_URL = "https://data-analysis-project-production.up.railway.app/data"

data = requests.get(API_URL).json()

capital = data["capital"]
capital_inicial = data["capital_inicial"]
historial = data["historial"]
posiciones = data["posiciones"]

# =========================
# KPIs
# =========================

pnl = capital - capital_inicial
pnl_pct = (pnl / capital_inicial) * 100

col1, col2, col3 = st.columns(3)

col1.metric("Capital", f"${capital:.2f}")
col2.metric("PnL", f"${pnl:.2f}", f"{pnl_pct:.2f}%")
col3.metric("Posiciones", len(posiciones))

# =========================
# HISTORIAL
# =========================

df = pd.DataFrame(historial)

if not df.empty:
    st.subheader("Historial trades")
    st.dataframe(df)

# =========================
# EQUITY CURVE
# =========================

equity = []

for h in historial:
    equity.append(h["capital"])

if equity:
    st.subheader("Equity Curve")
    st.line_chart(pd.DataFrame(equity, columns=["Capital"]))

# =========================
# POSICIONES
# =========================

st.subheader("Posiciones activas")

if posiciones:
    df_pos = pd.DataFrame(posiciones).T
    st.dataframe(df_pos)
else:
    st.info("No hay posiciones abiertas")