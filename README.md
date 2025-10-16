# 📊 Factor Investing Backtest

**A multi-factor long-short equity backtest implemented in Python.**  
This project builds, tests, and evaluates factor-based portfolios (Value, Momentum, Quality) on an S&P 500 universe and compares performance to the market benchmark (SPY).

---

## 🔎 Overview
The repository demonstrates:
- factor construction (momentum, value, quality),
- portfolio construction (long-short or long-only, monthly rebalancing),
- a backtesting engine with performance statistics (annualized return, volatility, Sharpe, max drawdown),
- basic robustness checks (lookahead avoidance, assertions for weights),
- light treatment of transaction costs and turnover.

This is intended as a reproducible portfolio project suitable for a quant-investing portfolio or interview discussion.

---

## 🧭 Project Structure
factor-investing-backtest/
│
├── data/                # (optional) cached market data
├── src/                 # Python scripts for modularity
│   ├── data_loader.py
│   ├── factor_model.py
│   └── backtest.py
├── results/             # Output plots, logs, or performance metrics
├──factor_backtest.ipynb
├── requirements.txt
└── README.md



---

## 🛠️ Requirements
Tested with Python 3.10+.

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# 🧩 How it works (high-level)

## 1. Data

Scrape current S&P 500 tickers from Wikipedia (utility in src/data_loader.py).

Download adjusted close prices (via yfinance).

Optionally fetch simple fundamentals via yfinance.Ticker.info (P/B, P/E, ROE).

## 2. Factors (src/factor_builder.py)

Momentum: 12-month return skipping the last month.

Value: inverse P/B or inverse P/E where available.

Quality: low historical volatility or ROE where available.

Cross-sectional z-score normalization per rebalance date.

Combine factors by equal weighting (or custom weights).

## 3. Portfolio construction (src/portfolio.py)

Monthly rebalance (e.g., end-of-month).

Long top X% and short bottom X% (e.g. 20% each) for long-short; equal weight per leg.

Expand rebalance weights to daily by forward-filling.

## 4. Backtest (src/backtest.py)

Compute daily P&L using previous-day weights and daily returns.

Metrics: cumulative returns, annualized return, volatility, Sharpe, max drawdown, rolling Sharpe.

Approximate transaction costs using turnover × cost per unit.