import streamlit as st
import requests
import pandas as pd

API_URL = "https://data-analysis-project-production.up.railway.app/data"

st.title("🚀 BOT CUANT PRO")

data = requests.get(API_URL).json()

capital = data.get("capital", 0)
posiciones = data.get("posiciones", {})
historial = data.get("historial", [])

st.metric("Capital", capital)
st.metric("Posiciones", len(posiciones))
st.metric("Trades", len(historial))

st.subheader("Posiciones")

rows = []
for s, p in posiciones.items():
    rows.append({
        "Symbol": s,
        "Inversión": p["inversion"],
        "Prob": p["prob"]
    })

if rows:
    st.dataframe(pd.DataFrame(rows))

st.subheader("Historial")

if historial:
    st.dataframe(pd.DataFrame(historial))