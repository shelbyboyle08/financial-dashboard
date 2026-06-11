# Project Notes — Talking Points

A reference for explaining how this project was built, what it uses, and why.

## What it is

A multi-page Streamlit dashboard that pulls live market and financial-statement
data for any public ticker and presents it through three lenses: price/technical
analysis, peer comparison, and fundamental/credit analysis (EBITDA, working
capital, leverage).

## Tech stack

| Tool | Role | Why this choice |
|---|---|---|
| **Python 3** | Core language | Standard for data work; huge ecosystem of finance/data libraries |
| **Streamlit** | Web app framework | Builds an interactive multi-page dashboard from plain Python — no separate frontend code, fast to iterate |
| **yfinance** | Data source | Free wrapper around Yahoo Finance's API — no API key needed, covers price history *and* financial statements |
| **pandas** | Data handling | All time-series and financial-statement data is manipulated as DataFrames (rolling averages, returns, ratios) |
| **Plotly** | Charting | Interactive charts (zoom, hover tooltips) embedded directly in Streamlit |
| **Git / GitHub** | Version control & hosting source | Standard workflow; also what Streamlit Cloud deploys from |
| **Streamlit Community Cloud** | Deployment | Free hosting that auto-redeploys on every push to `main` |

## Data sources

All data comes from **Yahoo Finance via `yfinance`**, fetched live (with caching):

- **Price history** (`Ticker.history`) — daily OHLCV (open/high/low/close/volume)
- **Company info** (`Ticker.info`) — company name, basic profile data
- **Income statement** (`Ticker.income_stmt`) — annual revenue, EBITDA, EBIT, net income, etc.
- **Balance sheet** (`Ticker.balance_sheet`) — annual assets, liabilities, working capital, debt, etc.

No static/sample datasets are used — everything reflects the real, current
financials of whatever ticker the user enters.

## Project structure

```
app.py                       # Main page: price history, SMAs, volume, returns
pages/
  1_Compare_Tickers.py        # Normalized multi-ticker price comparison
  2_Fundamentals.py           # EBITDA, working capital, leverage trends
src/
  data.py                      # Shared data-loading + calculation helpers (cached)
requirements.txt              # pandas, streamlit, yfinance, plotly
```

Streamlit's file-based routing (`pages/` directory) gives the multi-page
structure for free — no router or navigation code needed.

## Key features by page

**Main dashboard (`app.py`)**
- Current price, day high/low, volume, with day-over-day change
- Price chart with 20-day and 50-day simple moving averages (trend smoothing)
- Volume chart
- Cumulative return since the start of the selected period

**Compare Tickers**
- Multiple tickers normalized to a common starting index (=100) so stocks at
  very different price levels can be compared on relative performance

**Fundamentals**
- EBITDA and EBITDA margin trend (operating profitability)
- Working capital, current assets/liabilities, and current ratio (short-term liquidity)
- Net Debt / EBITDA (a core leverage/credit metric)
- Tooltips and captions explain what each metric means and why it matters

## Notable engineering decisions

- **Caching strategy** (`st.cache_data`): price history cached 4 hours,
  financial statements/company info cached 24 hours — financial statements
  only update quarterly/annually, so long caching avoids redundant API calls.
- **Rate-limit handling**: Yahoo Finance rate-limits requests from shared
  cloud IPs (a known issue with `yfinance` on platforms like Streamlit Cloud).
  Added retry-with-backoff for transient `YFRateLimitError`s, and friendly
  in-app error messages instead of raw tracebacks if it persists. This is a
  good "describe a bug you debugged" story — local testing worked fine, but
  the deployed app failed until the rate-limiting + caching fix was in place.
- **Graceful degradation**: the Fundamentals page checks which line items
  (e.g. `EBITDA`, `Working Capital`, `Net Debt`) are actually present for a
  given company before rendering each section, since financial-sector
  companies report balance sheets differently than non-financials.

## Deployment

- Code lives on GitHub (public repo), authenticated locally via SSH key.
- Streamlit Community Cloud is connected to the GitHub repo and auto-deploys
  `app.py` on every push to `main` — free for public repos.
