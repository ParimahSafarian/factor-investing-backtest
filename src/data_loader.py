# src/data_loader.py
import pandas as pd
import yfinance as yf
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests



def get_sp500_tickers() -> List[str]:
    """Scrape *current* S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    # Add a User-Agent header so Wikipedia accepts the request
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers).text

    # Parse the first table on the page
    table = pd.read_html(html)[0]

    # Extract company names and tickers
    # companies = table["Security"]
    tickers = table["Symbol"]
    
    # Clean tickers (e.g. BRK.B -> BRK-B)
    tickers = tickers.str.replace('.', '-', regex=False).tolist()
    # tickers = ['SPY'] + tickers  # add SPY ETF for market proxy
    return tickers

def download_price_data(tickers, start="2010-01-01", end=None, interval='1d', batch_size=80):
    """
    Download adjusted close prices for a list of tickers. Batches reduce yfinance issues.
    Returns prices DataFrame with columns = tickers.
    """
    all_parts = []
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"Downloading batch {i} -> {i+len(batch)}")
        data = yf.download(batch, start=start, end=end, interval=interval, threads=True)['Close']
        # if single ticker -> make dataframe
        if isinstance(data, pd.Series):
            data = data.to_frame(name=batch[0])
        all_parts.append(data)
        time.sleep(1)  # be gentle with the API
    prices = pd.concat(all_parts, axis=1)
    prices = prices.sort_index(axis=1)
    return prices

def get_fundamentals(tickers, fields=None, pause=0.3):
    """
    Fetch simple fundamentals via yfinance .info (slow). fields: list of keys like 'trailingPE', 'priceToBook', 'returnOnEquity'
    Returns DataFrame indexed by ticker.
    """
    if fields is None:
        fields = ['trailingPE', 'priceToBook', 'returnOnEquity']
    rows = []
    for t in tickers:
        try:
            info = yf.Ticker(t).info
        except Exception:
            info = {}
        row = {f: info.get(f, None) for f in fields}
        row['symbol'] = t
        rows.append(row)
        time.sleep(pause)
    df = pd.DataFrame(rows).set_index('symbol')
    return df


def _fetch_one_quarterly(t):
    """Fetch quarterly fundamentals for a single ticker. Returns (ticker, bvps, ttm_eps) or Nones."""
    bvps, ttm_eps = None, None
    try:
        tk = yf.Ticker(t)
        bs = tk.quarterly_balance_sheet
        inc = tk.quarterly_income_stmt

        shares = None
        if bs is not None and not bs.empty:
            equity = None
            for field in ['Stockholders Equity', 'Total Stockholder Equity',
                          'Common Stock Equity']:
                if field in bs.index:
                    equity = bs.loc[field]
                    break
            for field in ['Ordinary Shares Number', 'Share Issued']:
                if field in bs.index:
                    shares = bs.loc[field]
                    break
            if equity is not None and shares is not None:
                bvps = (equity / shares).dropna().sort_index()

        if inc is not None and not inc.empty and 'Net Income' in inc.index:
            ni = inc.loc['Net Income'].dropna().sort_index()
            ttm_ni = ni.rolling(4, min_periods=4).sum()
            if shares is not None:
                shares_sorted = shares.dropna().sort_index()
                shares_aligned = shares_sorted.reindex(ttm_ni.index, method='ffill')
                ttm_eps = (ttm_ni / shares_aligned).dropna()
    except Exception:
        pass
    return t, bvps, ttm_eps


def get_quarterly_fundamentals(tickers, max_workers=10):
    """
    Fetch quarterly balance sheet and income statement data via yfinance.
    Uses threading to parallelize requests.
    Returns two DataFrames:
      - book_value: DataFrame with columns=tickers, index=quarter dates (book value per share)
      - ttm_earnings: DataFrame with columns=tickers, index=quarter dates (trailing 12-month EPS)
    """
    bv_dict = {}
    eps_dict = {}
    done = 0
    total = len(tickers)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_one_quarterly, t): t for t in tickers}
        for future in as_completed(futures):
            t, bvps, ttm_eps = future.result()
            if bvps is not None:
                bv_dict[t] = bvps
            if ttm_eps is not None:
                eps_dict[t] = ttm_eps
            done += 1
            if done % 50 == 0 or done == total:
                print(f"Quarterly fundamentals: {done}/{total}")

    book_value = pd.DataFrame(bv_dict)
    ttm_earnings = pd.DataFrame(eps_dict)
    return book_value, ttm_earnings
