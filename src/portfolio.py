# src/portfolio.py
import pandas as pd
import numpy as np

def construct_long_short_weights(score_df: pd.DataFrame, long_pct=0.2, short_pct=0.2):
    """
    For each date (row) in score_df, create equal-weighted long/short weights.
    Returns DataFrame of weights (rows=dates, cols=tickers). Sum of each row = 0.
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
        n_short = max(1, int(np.floor(short_pct * n)))
        if n_long + n_short == 0:
            continue
        ranked = row.sort_values(ascending=False)
        longs = ranked.index[:n_long]
        shorts = ranked.index[-n_short:]
        if n_long > 0:
            weights.loc[date, longs] = 1.0 / n_long
        if n_short > 0:
            weights.loc[date, shorts] = -1.0 / n_short
    return weights

def expand_weights_to_daily(weights_rebalance: pd.DataFrame, price_index: pd.DatetimeIndex):
    """
    Convert rebalancing weights (index = rebalance dates) to daily weights by forward filling.
    """
    daily_weights = weights_rebalance.reindex(price_index, method='ffill').fillna(0.0)
    return daily_weights
