# Data dictionary

## Market data (provider: Yahoo Finance through yfinance)
- `Date`: timestamp associated with the historical bar.
- `Open`, `High`, `Low`, `Close`: instrument price values as returned by provider.
- `Volume`: traded volume where supplied by provider.
- `MA20`, `MA50`: rolling mean of closing price over 20 and 50 bars.
- `Daily Change %`: percentage difference between the last two closes.
- `Volatility 20d %`: standard deviation of daily percentage returns over up to 20 observations, annualization not applied.

## News data (provider: GDELT DOC API)
- `title`: article title returned by GDELT.
- `url`: publisher article URL.
- `source`: publisher/domain where available.
- `published_at`: timestamp supplied by GDELT.
- `sentiment`: lightweight lexicon score from -1 to +1; not a financial-grade sentiment model.

The app does not bundle fabricated market or news records. Results depend on live API availability.
