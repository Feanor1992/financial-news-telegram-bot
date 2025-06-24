"""
Logic that will be run on a schedule to send digests.
"""

import telegram
import asyncio
import logging
from database import get_all_users_with_tickers
from data_source import get_news_from_yfinance
from llm_processor import get_simple_summary
from config import TELEGRAM_BOT_TOKEN

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def log_digest_stats(stats):
    """
    Logs the statistics of the digest mailing.
    """
    logging.info(
        f"Mailing statistics: "
        f"Users processed: {stats['users_processed']}, "
        f"News sent: {stats['news_sent']}, "
        f"LLM calls: {stats['llm_calls']}, "
        f"Cache hits: {stats['cache_hits']}, "
        f"Sending errors: {stats['errors']}"
    )


async def send_daily_digest():
    """
    Main function to send the daily news digest.
    """
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    users = get_all_users_with_tickers()

    stats = {
        'users_processed': 0,
        'news_sent': 0,
        'llm_calls': 0,
        'cache_hits': 0,
        'errors': 0
    }

    logging.info(f"Starting digest mailing for {len(users)} users.")

    for user in users:
        stats['users_processed'] += 1
        chat_id = user['chat_id']
        language = user['language']
        tickers = user['tickers'].split(',') # GROUP_CONCAT returns a string

        logging.info(f"Processing user {chat_id} with tickers: {tickers}")

        message_parts = [f"News digest for you ({language}): \n"]
        has_new_content = False

        for ticker in tickers:
            news_list = get_news_from_yfinance(ticker)
            if not news_list:
                continue

            message_parts.append(f"\n--- 📈 *{ticker}* ---\n")
            news_found_for_ticker = False

            for news_item in news_list[:3]:  # Take only 3 recent news items for MVP
                summary, from_cache = get_simple_summary(news_item['title'], news_item['link'], language)

                if not from_cache:
                    stats['llm_calls'] += 1
                else:
                    stats['cache_hits'] += 1

                if summary:
                    news_found_for_ticker = True
                    has_new_content = True
                    stats['news_sent'] += 1
                    formatted_news = (
                        f"*{news_item['title']}*\n"
                        f"{summary}\n"
                        f"[Источник]({news_item['link']})\n"
                    )
                    message_parts.append(formatted_news)
                    await asyncio.sleep(1) # Small delay between LLM requests (if not from cache)
                else:
                    logging.warning(f"Failed to get summary for: {news_item['title']}")

            if not news_found_for_ticker:
                message_parts.append(f"_No new news found._\n")

        if has_new_content:
            final_message = '\n'.join(message_parts)
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=final_message,
                    parse_mode='Markdown'
                )
                logging.info(f"Digest successfully sent to user {chat_id}")
            except Exception as e:
                stats['errors'] += 1
                logging.error(f"Failed to send message to user {chat_id}: {e}")
        else:
            logging.info(f"No new content to send to user {chat_id}.")

        await asyncio.sleep(5) # Pause between processing different users

    log_digest_stats(stats)

