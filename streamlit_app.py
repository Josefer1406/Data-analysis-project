import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("🚀 BOT CUANT INSTITUCIONAL PRO")

# =========================
# CONEXIÓN AL BOT
# =========================

try:
    data = requests.get("http://localhost:8080/data").json()
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

capital = data.get("capital", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

# =========================
# KPIs PRINCIPALES
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("💰 Capital", f"${round(capital,2)}")
col2.metric("📊 Posiciones abiertas", len(posiciones))
col3.metric("📈 Total operaciones", len(historial))

# =========================
# POSICIONES ACTIVAS (FIX PRO)
# =========================

st.subheader("📊 Posiciones activas")

if posiciones:
    filas = []

    for symbol, data_pos in posiciones.items():
        fila = {
            "Symbol": symbol,
            "Inversión ($)": round(data_pos.get("inversion", 0), 2),
            "Precio entrada": round(data_pos.get("entry", 0), 2)
        }
        filas.append(fila)

    df_pos = pd.DataFrame(filas)
    st.dataframe(df_pos, use_container_width=True)

else:
    st.info("No hay posiciones abiertas")

# =========================
# HISTORIAL DE OPERACIONES (FIX PRO)
# =========================

st.subheader("📜 Historial de operaciones")

if historial:
    df_hist = pd.DataFrame(historial)

    # ordenar columnas de forma segura
    columnas = ["symbol", "tipo", "capital", "probabilidad"]
    columnas_presentes = [c for c in columnas if c in df_hist.columns]

    df_hist = df_hist[columnas_presentes]

    st.dataframe(df_hist, use_container_width=True)

else:
    st.info("Sin operaciones aún")

# =========================
# EQUITY CURVE (SIMULADA)
# =========================

st.subheader("📈 Evolución del capital")

if historial:
    equity = []
    capital_temp = 1000  # capital inicial

    for trade in historial:
        # solo aplicar pnl si es venta (luego lo mejoramos)
        if trade.get("tipo") == "SELL":
            capital_temp = trade.get("capital", capital_temp)

        equity.append(capital_temp)

    df_equity = pd.DataFrame({"Capital": equity})
    st.line_chart(df_equity)

else:
    st.info("No hay datos suficientes para graficar")

# =========================
# INFO EXTRA
# =========================

st.markdown("---")
st.subheader("🧠 Estado del sistema")

st.write(f"Capital actual: ${round(capital,2)}")
st.write(f"Posiciones abiertas: {len(posiciones)}")
st.write(f"Historial operaciones: {len(historial)}")

st.markdown("✅ Sistema operativo en modo institucional")