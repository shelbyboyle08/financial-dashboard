import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data import load_balance_sheet, load_income_statement

st.set_page_config(page_title="Fundamentals", layout="wide")
st.title("Company Fundamentals")
st.caption("Annual EBITDA, working capital, and leverage trends from company financial statements.")

ticker = st.sidebar.text_input("Ticker symbol", value="AAPL").upper().strip()

if not ticker:
    st.info("Enter a ticker symbol to get started.")
    st.stop()

income = load_income_statement(ticker)
balance = load_balance_sheet(ticker)

if income.empty or balance.empty:
    st.error(f"No financial statement data found for '{ticker}'.")
    st.stop()

years = sorted(set(income.columns) & set(balance.columns))

# Drop years with incomplete EBITDA data (yfinance often includes an extra
# oldest year with NaNs for derived line items like EBITDA).
if "EBITDA" in income.index:
    years = [y for y in years if pd.notna(income.loc["EBITDA", y])]

if not years:
    st.error(f"No usable financial statement years found for '{ticker}'.")
    st.stop()

labels = [d.strftime("%Y") for d in years]


def row(df, name):
    return df.loc[name, years] if name in df.index else None


ebitda = row(income, "EBITDA")
revenue = row(income, "Total Revenue")
working_capital = row(balance, "Working Capital")
current_assets = row(balance, "Current Assets")
current_liabilities = row(balance, "Current Liabilities")
net_debt = row(balance, "Net Debt")

col1, col2, col3, col4 = st.columns(4)

if ebitda is not None:
    col1.metric("EBITDA (latest FY)", f"${ebitda.iloc[-1] / 1e9:.2f}B")
if ebitda is not None and revenue is not None:
    col2.metric("EBITDA Margin", f"{ebitda.iloc[-1] / revenue.iloc[-1] * 100:.1f}%")
if working_capital is not None:
    col3.metric("Working Capital", f"${working_capital.iloc[-1] / 1e9:.2f}B")
if current_assets is not None and current_liabilities is not None:
    col4.metric("Current Ratio", f"{current_assets.iloc[-1] / current_liabilities.iloc[-1]:.2f}")

st.divider()

if ebitda is not None and revenue is not None:
    revenue_fig = go.Figure()
    revenue_fig.add_trace(go.Bar(x=labels, y=revenue / 1e9, name="Revenue ($B)"))
    revenue_fig.add_trace(go.Bar(x=labels, y=ebitda / 1e9, name="EBITDA ($B)"))
    revenue_fig.update_layout(title="Revenue vs EBITDA", barmode="group", yaxis_title="USD (Billions)")
    st.plotly_chart(revenue_fig, use_container_width=True)

    margin_fig = go.Figure()
    margin_fig.add_trace(go.Scatter(x=labels, y=ebitda / revenue * 100, mode="lines+markers", name="EBITDA Margin"))
    margin_fig.update_layout(title="EBITDA Margin", yaxis_title="Margin (%)")
    st.plotly_chart(margin_fig, use_container_width=True)

if current_assets is not None and current_liabilities is not None:
    wc_fig = go.Figure()
    wc_fig.add_trace(go.Bar(x=labels, y=current_assets / 1e9, name="Current Assets ($B)"))
    wc_fig.add_trace(go.Bar(x=labels, y=current_liabilities / 1e9, name="Current Liabilities ($B)"))
    if working_capital is not None:
        wc_fig.add_trace(go.Scatter(x=labels, y=working_capital / 1e9, mode="lines+markers", name="Working Capital ($B)"))
    wc_fig.update_layout(title="Working Capital Components", barmode="group", yaxis_title="USD (Billions)")
    st.plotly_chart(wc_fig, use_container_width=True)

    ratio_fig = go.Figure()
    ratio_fig.add_trace(go.Scatter(x=labels, y=current_assets / current_liabilities, mode="lines+markers", name="Current Ratio"))
    ratio_fig.update_layout(title="Current Ratio", yaxis_title="Ratio")
    st.plotly_chart(ratio_fig, use_container_width=True)

if net_debt is not None and ebitda is not None:
    lev_fig = go.Figure()
    lev_fig.add_trace(go.Scatter(x=labels, y=net_debt / ebitda, mode="lines+markers", name="Net Debt / EBITDA"))
    lev_fig.update_layout(title="Leverage: Net Debt / EBITDA", yaxis_title="x EBITDA")
    st.plotly_chart(lev_fig, use_container_width=True)

with st.expander("View raw income statement"):
    st.dataframe(income)

with st.expander("View raw balance sheet"):
    st.dataframe(balance)
