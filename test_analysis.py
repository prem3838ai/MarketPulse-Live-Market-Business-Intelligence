import pandas as pd
import pytest
from src.analysis import summarize_market
from src.market_data import normalize_ticker
from src.news_data import lexicon_sentiment


def test_normalize_ticker():
    assert normalize_ticker(" aapl ") == "AAPL"


def test_reject_blank_ticker():
    with pytest.raises(ValueError):
        normalize_ticker("  ")


def test_summary_values():
    result = summarize_market(pd.DataFrame({"Close": [100, 110, 121]}))
    assert result["latest_close"] == 121
    assert result["observations"] == 3
    assert result["baseline_next_session"] == pytest.approx(110.3333333)


def test_empty_market_rejected():
    with pytest.raises(ValueError):
        summarize_market(pd.DataFrame({"Close": []}))


def test_sentiment_is_bounded():
    assert lexicon_sentiment("strong growth and profit") == 1.0
    assert lexicon_sentiment("loss decline and risk") == -1.0
    assert -1 <= lexicon_sentiment("growth but risk") <= 1
