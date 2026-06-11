import plotly.graph_objects as go
import streamlit as st

from src.data import load_history, load_or_warn

st.set_page_config(page_title="Compare Tickers", layout="wide")
st.title("Compare Tickers")
st.caption(
    "Compares relative performance across tickers by indexing each one's price to 100 "
    "at the start of the period. This makes it easy to compare stocks with very "
    "different price levels on the same scale — a line above 100 means the stock is up "
    "since the start date, below 100 means it's down."
)

tickers_input = st.sidebar.text_input("Tickers (comma-separated)", value="AAPL, MSFT, GOOGL")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

if not tickers:
    st.info("Enter at least one ticker symbol.")
    st.stop()

fig = go.Figure()
for ticker in tickers:
    hist = load_or_warn(load_history, ticker, period)
    if hist.empty:
        st.warning(f"No data found for '{ticker}'.")
        continue
    normalized = hist["Close"] / hist["Close"].iloc[0] * 100
    fig.add_trace(go.Scatter(x=hist.index, y=normalized, name=ticker))

fig.update_layout(
    title="Normalized Price Comparison (Start = 100)",
    xaxis_title="Date",
    yaxis_title="Indexed Price",
)
st.plotly_chart(fig, use_container_width=True)
