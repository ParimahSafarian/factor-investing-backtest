# src/data_loader.py
import pandas as pd
import yfinance as yf
import time
from typing import List
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
