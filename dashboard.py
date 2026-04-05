import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Bot Trading LIVE (REAL TIME)")

url = "https://TU_URL/data"

try:
    df = pd.read_json(url)

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    ventas = df[df["tipo"] == "SELL"]

    col1, col2, col3 = st.columns(3)

    pnl_total = ventas["pnl"].sum()
    total_trades = len(ventas)

    win_rate = (
        len(ventas[ventas["pnl"] > 0]) / total_trades * 100
        if total_trades > 0 else 0
    )

    col1.metric("PnL Total", f"{pnl_total:.2f} USDT")
    col2.metric("Trades", total_trades)
    col3.metric("Win Rate", f"{win_rate:.2f}%")

    if not df.empty:
        st.metric("Capital actual", f"{df['capital'].iloc[-1]:.2f} USDT")

    st.line_chart(df.set_index("fecha")["capital"])

    st.dataframe(df)

except Exception as e:
    st.error(f"Error: {e}")