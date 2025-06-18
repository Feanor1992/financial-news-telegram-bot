"""
Module for all operations with the SQLite database.
"""

import sqlite3
import logging

DATABASE_NAME = 'bot_database.db'


def get_db_connection():
    """
    Creates a connection to the database.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database by creating the necessary tables.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Table to store users and their settings
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru',
                risk_profile TEXT DEFAULT 'moderate',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        # Table to store tickers a user is subscribed to
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS user_tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                ticker TEXT,
                FOREIGN KEY (chat_id) REFERENCES users (chat_id)
            '''
        )
        # Table for caching processed news and LLM responses
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS news_cache (
                url_hash TEXT PRIMARY KEY,
                processed_summary TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        conn.commit()
    logging.info('Database initialized.')


def add_or_update_user(chat_id, language='ru'):
    """
    Adds a new user or updates an existing one.
    """
    with get_db_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO users (chat_id, language) VALUES (?, ?)',
            (chat_id, language)
        )
        conn.commit()
    logging.info(f"User {chat_id} added or updated")


def add_ticker_for_user(chat_id, ticker):
    """
    Adds a ticker for a user.
    """
    ticker = ticker.upper()
    with get_db_connection() as conn:
        # Check if the subscription already exists
        exists = conn.execute(
            'SELECT 1 FROM user_tickers WHERE chat_id = ? AND ticker = ?',
            (chat_id, ticker)
        ).fetchone()
        if not exists:
            conn.execute(
                'INSERT INTO user_tickers (chat_id, ticker) VALUES (?, ?)',
                (chat_id, ticker)
            )
            conn.commit()
            logging.info(f"Ticker {ticker} added for user {chat_id}.")
            return True
    return False


def remove_ticker_for_user(chat_id, ticker):
    """
    Removes a ticker for a user.
    """
    ticker = ticker.upper()
    with get_db_connection() as conn:
        result = conn.execute(
            'DELETE FROM user_tickers WHERE chat_id = ? AND ticker = ?',
            (chat_id, ticker)
        )
        conn.commit()
        logging.info(f"Ticker {ticker} removed for user {chat_id}.")
        return result.rowcount > 0


def get_user_ticker(chat_id):
    """
    Returns a list of tickers for a user.
    :param chat_id:
    :return: list of tickers
    """
    with get_db_connection() as conn:
        tickers = conn.execute(
            'SELECT ticker From user_tickers WHERE chat_id = ?',
            (chat_id,)
        ).fetchall()
        return [row['ticker'] for row in tickers]


def get_all_users_with_tickers():
    """
    Returns all users and their subscriptions for the digest mailing.
    """
    with get_db_connection() as conn:
        query = """
            SELECT u.chat_id, u.language, GROUP_CONCAT(ut.ticker) as tickers
            FROM users u
            LEFT JOIN user_tickers ut ON u.chat_id = ut.chat_id
            WHERE ut.ticker IS NOT NULL
            GROUP BY u.chat_id, u.language
        """
        users = conn.execute(query).fetchall()
        return [dict(user) for user in users]


def get_summary_from_cache(url):
    """
    Checks the cache for a processed summary for a URL.
    :param url:
    :return: the summary if found, otherwise None.
    """
    import hashlib
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    with get_db_connection() as conn:
        result = conn.execute(
            'SELECT processed_summary FROM news_cache WHERE url_hash = ?',
            (url_hash,)
        ).fetchone()
        return result['processed_summary'] if result else None


def add_summary_to_cache(url, summary):
    """
    Adds a processed news summary to the cache.
    """
    import hashlib
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    with get_db_connection() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO news_cache (url_hash, processed_summary) VALUES (?, ?)',
            (url_hash, summary)
        )
        conn.commit()

