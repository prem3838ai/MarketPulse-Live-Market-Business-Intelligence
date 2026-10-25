from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.market_data import fetch_market_data, normalize_ticker
from src.news_data import fetch_news
from src.analysis import summarize_market

st.set_page_config(page_title="MarketPulse | Live Intelligence", page_icon="📈", layout="wide")
st.title("📈 MarketPulse")
st.caption("Live market data + global business news · Educational analytics, not investment advice")

with st.sidebar:
    st.header("Research settings")
    ticker = st.text_input("Ticker symbol", value="AAPL", help="Examples: AAPL, MSFT, NVDA, RELIANCE.NS, TCS.NS")
    period = st.selectbox("Historical range", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    st.divider()
    news_query = st.text_input("News topic / company", value="Apple Inc")
    news_limit = st.slider("News articles", 5, 30, 15)
    refresh = st.button("Refresh live data", type="primary", use_container_width=True)

if "market_cache" not in st.session_state or refresh:
    st.session_state.pop("market_cache", None)
if "news_cache" not in st.session_state or refresh:
    st.session_state.pop("news_cache", None)

try:
    clean_ticker = normalize_ticker(ticker)
    cache_key = f"{clean_ticker}:{period}"
    if cache_key not in st.session_state.get("market_cache", {}):
        with st.spinner(f"Fetching latest available data for {clean_ticker}…"):
            market = fetch_market_data(clean_ticker, period=period)
        st.session_state.setdefault("market_cache", {})[cache_key] = market
    market = st.session_state["market_cache"][cache_key]
    metrics = summarize_market(market)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest close", f"{metrics['latest_close']:,.2f}", f"{metrics['daily_change_pct']:+.2f}%")
    c2.metric("20-bar average", f"{metrics['ma20']:,.2f}")
    c3.metric("20-day volatility", f"{metrics['volatility_20d_pct']:.2f}%")
    c4.metric("Price observations", f"{metrics['observations']:,}")
    st.caption(f"Latest provider timestamp: {market['Date'].iloc[-1].strftime('%Y-%m-%d %H:%M UTC')} · Provider data may be delayed.")

    st.subheader(f"{clean_ticker} · Price and trend")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=market["Date"], y=market["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=market["Date"], y=market["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=market["Date"], y=market["MA50"], mode="lines", name="MA50"))
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=25, b=10), hovermode="x unified", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    if "Volume" in market.columns:
        vol_fig = go.Figure(go.Bar(x=market["Date"], y=market["Volume"], name="Volume"))
        vol_fig.update_layout(height=220, title="Reported volume", margin=dict(l=10, r=10, t=45, b=10))
        st.plotly_chart(vol_fig, use_container_width=True)
    with st.expander("Baseline estimate and methodology"):
        st.metric("Rolling-mean baseline for next session", f"{metrics['baseline_next_session']:,.2f}")
        st.write("This baseline is the mean of up to the last five closing prices. It is a naive benchmark for learning, not a validated forecast or trading recommendation.")
    st.download_button("Download market data CSV", market.to_csv(index=False).encode("utf-8"), file_name=f"{clean_ticker.lower()}_market_data.csv", mime="text/csv")
except Exception as exc:
    market = None
    st.error(f"Market data could not be loaded: {exc}")
    st.info("Check the ticker, internet connection, and provider availability. This app does not substitute fabricated sample values.")

st.divider()
st.subheader("📰 Live business news")
if st.button("Search latest news", use_container_width=False):
    try:
        with st.spinner("Querying GDELT news…"):
            st.session_state["news_results"] = fetch_news(news_query, news_limit)
    except Exception as exc:
        st.error(str(exc))
news = st.session_state.get("news_results")
if news is not None:
    if not news:
        st.warning("No articles returned. Try a broader company or topic query.")
    else:
        news_df = pd.DataFrame(news)
        st.caption(f"{len(news_df)} articles returned by GDELT · Sentiment is a simple word-list indicator.")
        for item in news:
            st.markdown(f"**[{item['title']}]({item['url']})**" if item["url"] else f"**{item['title']}**")
            st.caption(f"{item['source']} · {item['published_at']} · Lexicon sentiment: {item['sentiment']:+.2f}")
        st.download_button("Download news CSV", news_df.to_csv(index=False).encode("utf-8"), file_name="marketpulse_news.csv", mime="text/csv")
else:
    st.write("Enter a company or topic in the sidebar, then select **Search latest news**.")

st.divider()
st.caption("Sources: Yahoo Finance via yfinance; GDELT Project DOC API. Data availability, delay, and coverage are controlled by providers.")
