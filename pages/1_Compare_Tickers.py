import plotly.graph_objects as go
import streamlit as st

from src.data import load_history

st.set_page_config(page_title="Compare Tickers", layout="wide")
st.title("Compare Tickers")

tickers_input = st.sidebar.text_input("Tickers (comma-separated)", value="AAPL, MSFT, GOOGL")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

if not tickers:
    st.info("Enter at least one ticker symbol.")
    st.stop()

fig = go.Figure()
for ticker in tickers:
    hist = load_history(ticker, period)
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
