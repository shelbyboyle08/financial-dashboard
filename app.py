import plotly.graph_objects as go
import streamlit as st

from src.data import add_moving_averages, add_returns, load_history, load_info, load_or_stop

st.set_page_config(page_title="Financial Dashboard", layout="wide")
st.title("Financial Data Dashboard")

ticker = st.sidebar.text_input("Ticker symbol", value="AAPL").upper().strip()
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

if not ticker:
    st.info("Enter a ticker symbol to get started.")
    st.stop()

hist = load_or_stop(load_history, ticker, period)

if hist.empty:
    st.error(f"No data found for ticker '{ticker}'.")
    st.stop()

info = load_or_stop(load_info, ticker)
st.subheader(info.get("longName", ticker))

latest = hist.iloc[-1]
prev = hist.iloc[-2] if len(hist) > 1 else latest
change = latest["Close"] - prev["Close"]
pct_change = (change / prev["Close"]) * 100 if prev["Close"] else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Close", f"${latest['Close']:.2f}", f"{change:+.2f} ({pct_change:+.2f}%)")
col2.metric("Day High", f"${latest['High']:.2f}")
col3.metric("Day Low", f"${latest['Low']:.2f}")
col4.metric("Volume", f"{latest['Volume']:,.0f}")

hist = add_moving_averages(hist)
hist = add_returns(hist)

price_fig = go.Figure()
price_fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close"))
price_fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA20"], name="SMA 20"))
price_fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA50"], name="SMA 50"))
price_fig.update_layout(title=f"{ticker} Price History", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(price_fig, use_container_width=True)

volume_fig = go.Figure()
volume_fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume"))
volume_fig.update_layout(title=f"{ticker} Trading Volume", xaxis_title="Date", yaxis_title="Shares")
st.plotly_chart(volume_fig, use_container_width=True)

return_fig = go.Figure()
return_fig.add_trace(go.Scatter(x=hist.index, y=hist["Cumulative Return"] * 100, name="Cumulative Return"))
return_fig.update_layout(title=f"{ticker} Cumulative Return", xaxis_title="Date", yaxis_title="Return (%)")
st.plotly_chart(return_fig, use_container_width=True)

with st.expander("View raw data"):
    st.dataframe(hist)
