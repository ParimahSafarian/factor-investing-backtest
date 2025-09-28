# src/backtest.py
import pandas as pd
import numpy as np

def backtest(weights_daily: pd.DataFrame, prices: pd.DataFrame):
    """
    weights_daily: DataFrame indexed by ALL trading days, columns tickers (weights sum = 0)
    prices: adjusted close prices, same column set as weights
    Returns: strategy_returns (Series of daily returns)
    """
    daily_ret = prices.pct_change().fillna(0)
    # use yesterday's weights to compute today's P&L (no lookahead)
    aligned_weights = weights_daily.reindex(daily_ret.index).fillna(0)
    strat_ret = (aligned_weights.shift(1).fillna(0) * daily_ret).sum(axis=1)
    return strat_ret

def performance_stats(returns: pd.Series, trading_days=252):
    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    ann_return = returns.mean() * trading_days
    ann_vol = returns.std() * (trading_days**0.5)
    sharpe = ann_return / ann_vol if ann_vol != 0 else np.nan
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    max_drawdown = drawdown.min()
    stats = {
        'total_return': total_return,
        'ann_return': ann_return,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown
    }
    return stats, cumulative, drawdown

def rolling_sharpe(returns: pd.Series, window=252):
    rs = returns.rolling(window).mean() / returns.rolling(window).std() * (252**0.5)
    return rs
