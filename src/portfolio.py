# src/portfolio.py
import pandas as pd
import numpy as np

def construct_long_short_weights(score_df: pd.DataFrame, long_pct=0.2, short_pct=0.2,
                                  long_weight=1.0, short_weight=0.0):
    """
    For each date (row) in score_df, create equal-weighted long/short weights.
    long_pct/short_pct: fraction of tickers to go long/short.
    long_weight: total dollar weight on the long side (default 1.0 = fully invested).
    short_weight: total dollar weight on the short side (default 0.0 = long-only).
    Returns DataFrame of weights (rows=dates, cols=tickers).
    """
    dates = score_df.index
    cols = score_df.columns
    weights = pd.DataFrame(0.0, index=dates, columns=cols)

    for date in dates:
        row = score_df.loc[date].dropna()
        n = len(row)
        if n == 0:
            continue
        n_long = max(1, int(np.floor(long_pct * n)))
        n_short = max(1, int(np.floor(short_pct * n))) if short_weight > 0 else 0
        ranked = row.sort_values(ascending=False)
        longs = ranked.index[:n_long]
        if n_long > 0:
            weights.loc[date, longs] = long_weight / n_long
        if n_short > 0:
            shorts = ranked.index[-n_short:]
            weights.loc[date, shorts] = -short_weight / n_short
    return weights

def expand_weights_to_daily(weights_rebalance: pd.DataFrame, price_index: pd.DatetimeIndex):
    """
    Convert rebalancing weights (index = rebalance dates) to daily weights by forward filling.
    """
    daily_weights = weights_rebalance.reindex(price_index, method='ffill').fillna(0.0)
    return daily_weights
