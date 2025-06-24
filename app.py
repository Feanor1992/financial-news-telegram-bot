"""
Flask web application for the interactive part of the bot (command handling).
This file needs to be configured as a "Web App" on PythonAnywhere.
"""
import telegram
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
import database as db
import data_source as ds
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create Flask application
app = Flask(__name__)


# Asynchronous functions to handle commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    """
    chat_id = update.effective_chat.id
    try:
        db.add_or_update_user(chat_id)
        await update.message.reply_text(
            "Hello! I'm a financial news bot."
            "Use /help to see a list of commands."
        )
    except Exception as e:
        logging.error(f"Error in /start for {chat_id}: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /help command.
    """
    try:
        await update.message.reply_text(
        'Available commands: \n'
        '/start – Start interacting with the bot\n'
        '/add <TICKER> – Add a ticker to track (e.g., /add TSLA)\n'
        '/remove <TICKER> – Remove a ticker from the list (e.g., /remove GOOG)\n'
        '/list – Show the list of tracked tickers\n'
        '/help – Show this message'
        )
    except Exception as e:
        logging.error(f"Error in /help for {update.effective_chat.id}: {e}")


async def add_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /add command with ticker validation.
    """
    chat_id = update.effective_chat.id
    try:
        if not context.args:
            await update.message.reply_text('Please specify a ticker. Usage: /add <TICKER>')
            return

        ticker = context.args[0].upper()

        # Validate ticker
        if not ds.validate_ticker(ticker):
            await update.message.reply_text(f"Ticker '{ticker}' not found or invalid. Please check the spelling.")
            return

        if db.add_or_update_user(chat_id, ticker):
            await update.message.reply_text(f"Ticker {ticker} has been successfully added!")
        else:
            await update.message.reply_text(f"Ticker {ticker} is already in your list.")
    except Exception as e:
        logging.error(f"Error in /add for {chat_id}: {e}")


async def remove_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /remove command.
    """
    chat_id = update.effective_chat.id
    try:
        if not context.args:
            await update.message.reply_text('Please specify a ticker. Usage: /remove <TICKER>')
            return
        ticker = context.args[0]
        if db.remove_ticker_for_user(chat_id, ticker):
             await update.message.reply_text(f"Ticker {ticker.upper()} has been removed from your list.")
        else:
             await update.message.reply_text(f"Ticker {ticker.upper()} was not found in your list.")
    except Exception as e:
        logging.error(f"Error in /remove for {chat_id}: {e}")


async def list_tickers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /list command.
    """
    chat_id = update.effective_chat.id
    try:
        tickers = db.get_user_ticker(chat_id)
        if tickers:
            await update.message.reply_text('Your tracked tickers:\n' + '\n'.join(tickers))
        else:
            await update.message.reply_text("You don't have any tracked tickers yet. Add one using /add <TICKER>.")
    except Exception as e:
        logging.error(f"Error in /list for {chat_id}: {e}")


# Create the python-telegram-bot Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
# Add command handlers
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('add', add_ticker))
application.add_handler(CommandHandler('remove', remove_ticker))
application.add_handler(CommandHandler('list', list_tickers))


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint for the Telegram webhook, compatible with PTB v21+.
    """
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        # Create a task to process the update asynchronously,
        # so we don't block the webhook response.
        asyncio.create_task(application.process_update(update))
        return 'ok'
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return 'error', 500


@app.route('/')
def index():
    return 'Bot is running!'


if __name__ == '__main__':
    # IMPORTANT: This part will not run on PythonAnywhere.
    # It is executed via a WSGI server.
    # This part is for local testing.
    db.init_db()
    # Run the Flask application for local development
    # For production on PythonAnywhere, a WSGI server like gunicorn is used
    app.run(debug=True, port=5001)
