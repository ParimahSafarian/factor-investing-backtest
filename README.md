# Factor Investing Backtest

A multi-factor equity backtest on S&P 500 stocks, built in Python.

## Project Structure

```
src/
  data_loader.py      # S&P 500 tickers, price downloads, quarterly fundamentals
  factor_builder.py   # Factor computation and normalization
  portfolio.py        # Portfolio weight construction
  backtest.py         # Backtest engine and performance metrics
factor_backtest.ipynb # Main notebook — run everything here
```

## Factors

All factors are computed from price data:

- **Momentum** — 12-month return, skipping the most recent month
- **Reversal** — negated 1-month return (short-term mean reversion)
- **Quality** — negated rolling volatility (low vol = higher quality)
- **Beta** — negated rolling CAPM beta vs SPY (low beta = higher score)

Each factor is z-scored cross-sectionally before combining.

## Portfolio Construction

- Monthly rebalance (end-of-month)
- Long top N% of stocks by composite score, short bottom N%
- `long_weight` / `short_weight` control dollar exposure per side
- Defaults to long-only (`short_weight=0`)
- Weights forward-filled to daily frequency

## Backtest

- Daily P&L from previous-day weights x daily returns (no lookahead)
- Metrics: annualized return, volatility, Sharpe ratio, max drawdown
- Approximate transaction costs via turnover

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run `factor_backtest.ipynb`.
