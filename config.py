# Configuration management and loading of secret keys.
import os

# Load the token for the Telegram bot from environment variables.
# On PythonAnywhere, it needs to be set in the "Web" -> "Environment variables" section
# or as an environment variable for your console.


def load_config():
    """
    Loads configuration from secrets.py file (for local development)
    or from environment variables (for production)
    """
    try:
        # Try to load secrets from local secrets.py file
        # This file should be added to .gitignore and not committed to repository
        from secrets import TELEGRAM_TOKEN, GOOGLE_API_KEY
        print("Configuration loaded from local secrets.py file")
        return TELEGRAM_TOKEN, GOOGLE_API_KEY

    except ImportError:
        # If secrets.py file is not found, load from environment variables
        print("secrets.py file not found, loading from environment variables")

        # Load the token for the Telegram bot from environment variables.
        # On PythonAnywhere, it needs to be set in the "Web" -> "Environment variables" section
        # or as an environment variable for your console.
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token:
            raise ValueError('The TELEGRAM_BOT_TOKEN environment variable must be set or create secrets.py file')

        # Load the API key for Google Generative AI.
        # Fixed: added parameter to os.getenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError('The GOOGLE_API_KEY environment variable must be set or create secrets.py file')

        return telegram_token, google_api_key


# Load configuration when module is imported
TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY = load_config()

# Additional check in case values are empty
if not TELEGRAM_BOT_TOKEN:
    raise ValueError('TELEGRAM_BOT_TOKEN cannot be empty')

if not GOOGLE_API_KEY:
    raise ValueError('GOOGLE_API_KEY cannot be empty')
