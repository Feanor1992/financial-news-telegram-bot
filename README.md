# AI-Powered Financial News Bot for Telegram

This project is a Telegram bot created to help investors manage information overload by providing daily digests of financial news for their selected stock tickers. The bot operates in both English and Russian and is built with a strong focus on resource optimization to run exclusively on free-tier cloud services like PythonAnywhere.

## Core Features: ##

- **Customizable News Feed:** Users can add or remove any stock tickers to personalize their news digest.
- **AI-Powered Summaries:** Leverages Google's Generative AI (`gemini-2.0-flash`) to generate concise news summaries and analyze the potential impact on stocks.
- **News Scoring & Categorization:** Each news item is scored for importance (1-10) and categorized (e.g., M&A, earnings) to help users quickly identify what matters most.
- **Bilingual Support:** Provides news digests and analysis in both English and Russian, which can be configured by the user.
- **Interactive Components:** Features interactive buttons for quick actions like providing feedback or getting links to charts.

## Tech Stack: ##
- **Backend:** Python
- **Hosting:** PythonAnywhere (Free Tier) 
- **Database:** SQLite 
- **Data Sources:** `yfinance` , Alpha Vantage (Free Tier) , NewsAPI (Free Tier) , RSS Feeds (`feedparser`) 
- **AI & NLP:** Google Generative AI , `sumy` for pre-summarization 
- **Bot Framework:** `python-telegram-bot` with a `Flask` webhook for commands 

## Project Status: ##
This is currently an Minimum Viable Product  with a clear roadmap for future enhancements, including sentiment momentum tracking, earnings calendar integration, and price alerts.
