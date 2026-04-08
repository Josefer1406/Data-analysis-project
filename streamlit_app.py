 import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 BOT CUANT INSTITUCIONAL PRO")

# =========================
# URL API (IMPORTANTE)
# =========================

API_URL = "https://data-analysis-project-production.up.railway.app/data"
# Si usas Railway, cambia por:
# API_URL = "https://tu-app.railway.app/data"

# =========================
# CONEXIÓN
# =========================

try:
    response = requests.get(API_URL, timeout=5)
    data = response.json()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# Validación extra
if not isinstance(data, dict):
    st.error("❌ Respuesta inválida del servidor")
    st.stop()

capital = data.get("capital", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

# =========================
# KPIs
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("💰 Capital", f"${round(float(capital),2)}")
col2.metric("📊 Posiciones", len(posiciones))
col3.metric("📈 Trades", len(historial))

# =========================
# POSICIONES (100% SAFE)
# =========================

st.subheader("📊 Posiciones activas")

try:
    filas_pos = []

    if isinstance(posiciones, dict):
        for symbol, p in posiciones.items():
            if isinstance(p, dict):
                filas_pos.append({
                    "Symbol": symbol,
                    "Inversión": float(p.get("inversion", 0)),
                    "Entry": float(p.get("entry", 0))
                })

    if filas_pos:
        df_pos = pd.DataFrame(filas_pos)
        st.dataframe(df_pos, use_container_width=True)
    else:
        st.info("No hay posiciones abiertas")

except Exception as e:
    st.error(f"Error en posiciones: {e}")

# =========================
# HISTORIAL (100% SAFE)
# =========================

st.subheader("📜 Historial de operaciones")

try:
    filas_hist = []

    if isinstance(historial, list):
        for h in historial:
            if isinstance(h, dict):
                filas_hist.append({
                    "Symbol": h.get("symbol"),
                    "Tipo": h.get("tipo"),
                    "Capital": float(h.get("capital", 0)),
                    "Probabilidad": h.get("probabilidad")
                })

    if filas_hist:
        df_hist = pd.DataFrame(filas_hist)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Sin operaciones aún")

except Exception as e:
    st.error(f"Error en historial: {e}")

# =========================
# EQUITY CURVE
# =========================

st.subheader("📈 Evolución del capital")

try:
    equity = []

    if isinstance(historial, list):
        for h in historial:
            if isinstance(h, dict) and h.get("tipo") == "SELL":
                equity.append(float(h.get("capital", 0)))

    if equity:
        df_equity = pd.DataFrame({"Capital": equity})
        st.line_chart(df_equity)
    else:
        st.info("No hay suficientes datos de ventas")

except Exception as e:
    st.error(f"Error en equity: {e}")

# =========================
# DEBUG (CLAVE)
# =========================

with st.expander("🛠 Ver datos crudos"):
    st.json(data)