# src/factor_builder.py
import pandas as pd
import numpy as np

def compute_momentum(prices: pd.DataFrame, lookback_days=252, skip_days=21):
    """12-month momentum excluding most recent month: return_{t-252,t} shifted by skip_days."""
    mom = prices.pct_change(periods=lookback_days).shift(skip_days)
    return mom

def compute_volatility(prices: pd.DataFrame, window=252):
    """Annualized (approx) rolling volatility (daily returns std)"""
    daily_ret = prices.pct_change()
    vol = daily_ret.rolling(window).std() * np.sqrt(252)  # optional annualization
    return vol

def compute_quality_from_vol(prices: pd.DataFrame, window=252):
    """Quality proxy: lower historical volatility => higher quality """
    vol = compute_volatility(prices, window=window)
    quality = -vol  # higher = better
    return quality

def value_from_fundamentals(fund_df: pd.DataFrame):
    """
    Build a simple 'value' factor from fundamentals DataFrame (index=ticker).
    Returns Series or DataFrame with higher = better value.
    Prefer priceToBook if available; else invert trailingPE.
    """
    if 'priceToBook' in fund_df.columns and fund_df['priceToBook'].notna().any():
        val = -fund_df['priceToBook']  # lower P/B is better -> negate so larger is better
    elif 'trailingPE' in fund_df.columns and fund_df['trailingPE'].notna().any():
        val = -fund_df['trailingPE']   # lower PE = better
    else:
        val = pd.Series(index=fund_df.index, dtype=float)
    return val

def cross_sectional_zscore(factor_df: pd.DataFrame):
    """
    Compute z-score across tickers for each date (row-wise).
    factor_df: DataFrame with index = dates, columns = tickers
    """
    mean = factor_df.mean(axis=1)
    std = factor_df.std(axis=1).replace(0, np.nan)
    z = (factor_df.sub(mean, axis=0)).div(std, axis=0)
    return z

def combine_factors(factor_dfs: dict, weights: dict = None):
    """
    Combine multiple factor DataFrames (same index/columns expected).
    factor_dfs: {'mom': df, 'val': df, ...}
    weights: optional dict of same keys -> float
    """
    names = list(factor_dfs.keys())
    if weights is None:
        weights = {n: 1.0/len(names) for n in names}
    # align indexes/columns (take union)
    all_idx = sorted({d.index for d in factor_dfs.values()}, key=lambda x: x)
    # simpler: reindex to union of indexes and columns of first df
    base = list(factor_dfs.values())[0]
    common_index = base.index
    common_cols = base.columns
    # reindex all
    aligned = [factor_dfs[n].reindex(index=common_index, columns=common_cols) for n in names]
    score = sum(weights[n] * aligned[i] for i,n in enumerate(names))
    return score
