"""
Module for interacting with the LLM (Google Generative AI).
"""

import google.generativeai as genai
from config import GOOGLE_API_KEY
from database import get_summary_from_cache, add_summary_to_cache
import logging
import time

# Configure the API
genai.configure(api_key=GOOGLE_API_KEY)
# Use the model specified in the project document.
model = genai.GenerativeModel('gemini-2.5-flash')


def get_simple_summary(news_title, news_link, language='ru', max_retries=3):
    """
    Creates a simple news summary using the LLM, with caching and a retry mechanism.
    """
    # 1. Check the cache
    cached_summary = get_summary_from_cache(news_link)
    if cached_summary:
        logging.info(f"Found summary in cache for: {news_link}")
        return cached_summary, True  # True means the result is from the cache

    # 2. If not in cache, generate a new summary
    logging.info(f"Generating new summary for: {news_title}")
    if language == 'ru':
        prompt = f"""
        Выступи в роли финансового аналитика. Проанализируй следующий заголовок финансовой новости: "{news_title}".
        Твоя задача:
        1. Кратко пересказать суть новости на русском языке в одном предложении.
        2. Оценить потенциальное влияние (Позитивное, Нейтральное, Негативное) на акции компании.
        3. Дать очень краткий прогноз на 1-3 дня.
        Ответь строго в формате:
        СУТЬ: [Твой пересказ]
        ВЛИЯНИЕ: [Твоя оценка]
        ПРОГНОЗ: [Твой прогноз]
        """
    else:
        prompt = f"""
        Act as a financial analyst. Analyze the following financial news headline: "{news_title}".
        Your task:
        1. Briefly summarize the news essence in one sentence in English.
        2. Assess the potential impact (Positive, Neutral, Negative) on the company's stock.
        3. Provide a very short-term forecast (1-3 days).
        Respond strictly in the format:
        ESSENCE: [Your summary]
        IMPACT: [Your assessment]
        FORECAST: [Your forecast]
        """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            summary = response.text
            # 3. Save the new summary to the cache
            add_summary_to_cache(news_link, summary)
            return summary, False  # False means the result is not from the cache
        except Exception as e:
            logging.error(f"Error interacting with Google Generative AI (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # Exponential backoff
                time.sleep(2 ** attempt)
            else:
                logging.error("All LLM attempts have been exhausted.")
                # Fallback: return a simple text if the LLM fails
                fallback_summary = "Failed to analyze the news with AI."
                return fallback_summary, False

    return None, False
