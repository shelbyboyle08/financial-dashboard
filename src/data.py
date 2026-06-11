import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=3600)
def load_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    return yf.Ticker(ticker).history(period=period)


@st.cache_data(ttl=3600)
def load_info(ticker: str) -> dict:
    return yf.Ticker(ticker).info


@st.cache_data(ttl=3600)
def load_income_statement(ticker: str) -> pd.DataFrame:
    return yf.Ticker(ticker).income_stmt


@st.cache_data(ttl=3600)
def load_balance_sheet(ticker: str) -> pd.DataFrame:
    return yf.Ticker(ticker).balance_sheet


def add_moving_averages(df: pd.DataFrame, windows=(20, 50)) -> pd.DataFrame:
    df = df.copy()
    for window in windows:
        df[f"SMA{window}"] = df["Close"].rolling(window).mean()
    return df


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Daily Return"] = df["Close"].pct_change()
    df["Cumulative Return"] = (1 + df["Daily Return"]).cumprod() - 1
    return df
