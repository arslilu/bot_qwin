import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OSAGO_API_KEY = os.getenv("OSAGO_API_KEY")
FINES_API_KEY = os.getenv("FINES_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable.")
if not OSAGO_API_KEY:
    raise ValueError("Missing OSAGO_API_KEY environment variable.")
if not FINES_API_KEY:
    # Fines API key is the same as OSAGO in the provided example, but good to keep separate for future flexibility
    raise ValueError("Missing FINES_API_KEY environment variable.")

