from __future__ import annotations
import pandas as pd


def summarize_market(frame: pd.DataFrame) -> dict:
    if frame is None or frame.empty or "Close" not in frame:
        raise ValueError("Market data must contain at least one Close value.")
    close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
    if close.empty:
        raise ValueError("Market data has no valid closing prices.")
    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else latest
    change = ((latest / previous) - 1) * 100 if previous else 0.0
    returns = close.pct_change().dropna().tail(20)
    volatility = float(returns.std(ddof=1) * 100) if len(returns) > 1 else 0.0
    ma20 = float(close.tail(20).mean())
    baseline = float(close.tail(min(5, len(close))).mean())
    return {"latest_close": latest, "daily_change_pct": change, "volatility_20d_pct": volatility, "ma20": ma20, "baseline_next_session": baseline, "observations": int(len(close))}
