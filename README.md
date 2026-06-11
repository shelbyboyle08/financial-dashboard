# my-python-project

A financial data dashboard built with Streamlit, using live market data from Yahoo Finance (`yfinance`).

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

- Main page: enter a ticker symbol to see price history, moving averages, volume, and cumulative returns.
- "Compare Tickers" page: compare normalized price performance across multiple tickers.

## Project structure

- `app.py` — main dashboard page
- `pages/` — additional Streamlit pages (e.g. ticker comparison)
- `src/` — shared data-loading and calculation helpers
- `data/raw/`, `data/processed/` — for any local datasets
- `notebooks/` — Jupyter notebooks for exploration
- `tests/` — tests for code in `src/`
