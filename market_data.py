from __future__ import annotations
import pandas as pd


def normalize_ticker(ticker: str) -> str:
    value = ticker.strip().upper()
    if not value or len(value) > 30 or any(c.isspace() for c in value):
        raise ValueError("Enter a valid ticker symbol, for example AAPL, MSFT, or RELIANCE.NS.")
    return value


def fetch_market_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch latest available OHLCV data. Raises clear errors; never fabricates data."""
    import yfinance as yf
    ticker = normalize_ticker(ticker)
    frame = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if frame is None or frame.empty:
        raise RuntimeError(f"No market data returned for {ticker}. Check the ticker/provider or try later.")
    frame = frame.reset_index()
    frame.columns = [str(c).replace(" ", "_") for c in frame.columns]
    date_col = "Date" if "Date" in frame.columns else frame.columns[0]
    frame = frame.rename(columns={date_col: "Date"})
    required = {"Date", "Close"}
    if not required.issubset(frame.columns):
        raise RuntimeError("Market provider returned an unexpected data format.")
    frame["Date"] = pd.to_datetime(frame["Date"], utc=True, errors="coerce")
    frame = frame.dropna(subset=["Date", "Close"]).sort_values("Date")
    for col in ("Open", "High", "Low", "Close", "Volume"):
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["MA20"] = frame["Close"].rolling(20, min_periods=1).mean()
    frame["MA50"] = frame["Close"].rolling(50, min_periods=1).mean()
    frame["Return"] = frame["Close"].pct_change()
    return frame.reset_index(drop=True)
