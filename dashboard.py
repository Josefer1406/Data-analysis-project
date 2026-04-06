import streamlit as st
import pandas as pd
import numpy as np

st.title("QUANT FUND DASHBOARD")

df = pd.read_json("https://data-analysis-project-production.up.railway.app/data")

df["fecha"] = pd.to_datetime(df["fecha"])
df = df.sort_values("fecha")

capital = df["capital"]
returns = capital.pct_change().dropna()

roll = capital.cummax()
dd = (capital-roll)/roll

sharpe = (returns.mean()/returns.std())*np.sqrt(252)

st.metric("Sharpe", round(sharpe,2))
st.metric("Drawdown", round(dd.min()*100,2))
st.metric("PnL", round(df["pnl"].sum(),2))

st.line_chart(capital)
st.area_chart(dd)
st.dataframe(df)