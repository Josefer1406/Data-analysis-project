import streamlit as st
import pandas as pd
import numpy as np

st.title("HEDGE FUND DASHBOARD")

url = "https://data-analysis-project-production.up.railway.app/data"
df = pd.read_json(url)

df["fecha"] = pd.to_datetime(df["fecha"])
df = df.sort_values("fecha")

capital = df["capital"]
returns = capital.pct_change().dropna()

ventas = df[df["tipo"]=="SELL"]

pnl = ventas["pnl"].sum()
wr = len(ventas[ventas["pnl"]>0])/len(ventas) if len(ventas)>0 else 0

roll = capital.cummax()
dd = (capital-roll)/roll

sharpe = (returns.mean()/returns.std())*np.sqrt(252) if returns.std()!=0 else 0

st.metric("PnL", round(pnl,2))
st.metric("WinRate", round(wr*100,2))
st.metric("Drawdown", round(dd.min()*100,2))
st.metric("Sharpe", round(sharpe,2))

st.line_chart(capital)
st.area_chart(dd)
st.dataframe(df)