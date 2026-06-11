import time

import pandas as pd
import streamlit as st
import yfinance as yf
from yfinance.exceptions import YFRateLimitError


class RateLimitedError(Exception):
    """Raised when Yahoo Finance keeps rate-limiting requests after retries."""


def _with_retry(fn, retries=3, base_delay=1):
    for attempt in range(retries):
        try:
            return fn()
        except YFRateLimitError:
            if attempt == retries - 1:
                raise RateLimitedError(
                    "Yahoo Finance is rate-limiting requests right now. "
                    "Please wait a minute and try again."
                )
            time.sleep(base_delay * (2 ** attempt))


def load_or_stop(loader, *args, **kwargs):
    """Run a loader, showing a friendly error and halting the page on rate limits."""
    try:
        return loader(*args, **kwargs)
    except RateLimitedError as e:
        st.error(str(e))
        st.stop()


def load_or_warn(loader, *args, **kwargs):
    """Run a loader, showing a warning and returning an empty DataFrame on rate limits."""
    try:
        return loader(*args, **kwargs)
    except RateLimitedError as e:
        st.warning(str(e))
        return pd.DataFrame()


@st.cache_data(ttl=4 * 3600, show_spinner="Loading price history...")
def load_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    return _with_retry(lambda: yf.Ticker(ticker).history(period=period))


@st.cache_data(ttl=24 * 3600, show_spinner="Loading company info...")
def load_info(ticker: str) -> dict:
    return _with_retry(lambda: yf.Ticker(ticker).info)


@st.cache_data(ttl=24 * 3600, show_spinner="Loading income statement...")
def load_income_statement(ticker: str) -> pd.DataFrame:
    return _with_retry(lambda: yf.Ticker(ticker).income_stmt)


@st.cache_data(ttl=24 * 3600, show_spinner="Loading balance sheet...")
def load_balance_sheet(ticker: str) -> pd.DataFrame:
    return _with_retry(lambda: yf.Ticker(ticker).balance_sheet)


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
