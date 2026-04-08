import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 BOT CUANT PRO (HEDGE MODE)")

API_URL = "https://data-analysis-project-production.up.railway.app/data"

# =========================
# DATA
# =========================
try:
    data = requests.get(API_URL, timeout=5).json()
except:
    st.error("Error conectando al bot")
    st.stop()

capital = data.get("capital", 0)
capital_inicial = data.get("capital_inicial", 0)
pnl = data.get("pnl", 0)
pnl_pct = data.get("pnl_pct", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

# =========================
# KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Capital actual", f"${capital}")
col2.metric("🏦 Capital inicial", f"${capital_inicial}")
col3.metric("📈 PnL", f"${pnl}")
col4.metric("📊 % Retorno", f"{pnl_pct}%")

# =========================
# POSICIONES
# =========================
st.subheader("📊 Posiciones activas")

if posiciones:
    filas = []
    for s, p in posiciones.items():
        filas.append({
            "Symbol": s,
            "Inversión": round(p.get("inversion", 0), 2),
            "Entrada": round(p.get("entry", 0), 4),
            "Prob": round(p.get("prob", 0), 2)
        })

    st.dataframe(pd.DataFrame(filas), use_container_width=True)
else:
    st.info("Sin posiciones abiertas")

# =========================
# HISTORIAL
# =========================
st.subheader("📜 Historial")

if historial:
    df = pd.DataFrame(historial)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Sin operaciones aún")

# =========================
# EQUITY CURVE
# =========================
st.subheader("📈 Equity Curve")

if historial:
    equity = [capital_inicial]

    for h in historial:
        if h.get("tipo") == "SELL":
            equity.append(h.get("capital", capital_inicial))

    df_equity = pd.DataFrame({"Capital": equity})
    st.line_chart(df_equity)
else:
    st.info("Aún no hay datos para gráfica")

# =========================
# DEBUG
# =========================
with st.expander("🛠 Debug"):
    st.json(data)