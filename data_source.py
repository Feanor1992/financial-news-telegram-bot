"""
Module for fetching news from external sources.
"""

import yfinance as yf
import logging


def get_news_from_yfinance(ticker):
    """
    Fetches news for a given ticker from Yahoo Finance.
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            logging.info(f"No news found for ticker {ticker} on Yahoo Finance.")
            return []
        return [{'title': item['title'], 'link': item['link']} for item in news]
    except Exception as e:
        logging.error(f"Error fetching news for {ticker} from yfinance: {e}")
        return []


def validate_ticker(ticker):
    """
    Checks if a ticker exists using yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        # If the ticker has a 'shortName' or 'symbol', it's considered valid.
        # stock.info can be empty for invalid tickers or cause an error.
        if stock.info.get('shortName') or stock.info.get('symbol'):
            return True
        # Sometimes .info is empty but the ticker exists, let's try another method.
        hist = stock.history(period='1d')
        if not hist.empty:
            return True
        return False
    except Exception as e:
        logging.warning(f"Error validating ticker {ticker}: {e}")
        return False
