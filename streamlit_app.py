import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 BOT CUANT HEDGE FUND DASHBOARD")

API_URL = "https://data-analysis-project-production.up.railway.app/data"

# =========================
# DATA
# =========================
try:
    data = requests.get(API_URL, timeout=5).json()
except:
    st.error("❌ Error conectando al bot")
    st.stop()

capital = data.get("capital", 0)
capital_inicial = data.get("capital_inicial", 0)
pnl = data.get("pnl", 0)
pnl_pct = data.get("pnl_pct", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

# =========================
# KPIs PRINCIPALES
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Capital actual", f"${round(capital,2)}")
col2.metric("🏦 Capital inicial", f"${round(capital_inicial,2)}")
col3.metric("📈 PnL", f"${round(pnl,2)}")
col4.metric("📊 Retorno %", f"{round(pnl_pct,2)}%")

st.divider()

# =========================
# MÉTRICAS AVANZADAS
# =========================
st.subheader("🧠 Métricas de performance")

if historial:
    df = pd.DataFrame(historial)

    total_trades = len(df)
    wins = len(df[df["pnl"] > 0])
    losses = len(df[df["pnl"] <= 0])

    winrate = (wins / total_trades) * 100 if total_trades > 0 else 0

    avg_win = df[df["pnl"] > 0]["pnl"].mean() if wins > 0 else 0
    avg_loss = df[df["pnl"] <= 0]["pnl"].mean() if losses > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📊 Trades", total_trades)
    col2.metric("✅ Winrate", f"{round(winrate,2)}%")
    col3.metric("📈 Avg Win", round(avg_win, 4))
    col4.metric("📉 Avg Loss", round(avg_loss, 4))

else:
    st.info("Sin datos aún")

st.divider()

# =========================
# POSICIONES ACTIVAS
# =========================
st.subheader("📊 Posiciones activas")

if posiciones:
    filas = []

    for s, p in posiciones.items():
        entry = p.get("entry", 0)
        actual = p.get("max_precio", entry)
        pnl_pos = ((actual - entry) / entry) if entry > 0 else 0

        filas.append({
            "Symbol": s,
            "Inversión": round(p.get("inversion", 0), 2),
            "Entrada": round(entry, 4),
            "Máx precio": round(actual, 4),
            "PnL %": round(pnl_pos * 100, 2),
            "Prob": round(p.get("prob", 0), 2)
        })

    df_pos = pd.DataFrame(filas)
    st.dataframe(df_pos, use_container_width=True)

else:
    st.info("Sin posiciones abiertas")

st.divider()

# =========================
# HISTORIAL
# =========================
st.subheader("📜 Historial de trades")

if historial:
    df_hist = pd.DataFrame(historial)
    st.dataframe(df_hist, use_container_width=True)
else:
    st.info("Sin operaciones aún")

st.divider()

# =========================
# EQUITY CURVE
# =========================
st.subheader("📈 Equity Curve (Capital)")

if historial:
    equity = [capital_inicial]

    for h in historial:
        if h.get("tipo") == "SELL":
            equity.append(h.get("capital", capital_inicial))

    df_equity = pd.DataFrame({"Capital": equity})
    st.line_chart(df_equity)
else:
    st.info("Sin suficientes datos")

# =========================
# DISTRIBUCIÓN DE PNL
# =========================
st.subheader("📊 Distribución de PnL")

if historial:
    df_hist = pd.DataFrame(historial)
    st.bar_chart(df_hist["pnl"])
else:
    st.info("Sin datos")

# =========================
# EVOLUCIÓN DE TRADES
# =========================
st.subheader("📉 Evolución trade a trade")

if historial:
    df_hist = pd.DataFrame(historial)

    acumulado = df_hist["pnl"].cumsum()
    df_acc = pd.DataFrame({"PnL acumulado": acumulado})

    st.line_chart(df_acc)
else:
    st.info("Sin datos")

# =========================
# DEBUG
# =========================
with st.expander("🛠 Datos crudos"):
    st.json(data)