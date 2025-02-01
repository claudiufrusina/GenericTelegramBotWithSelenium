import os
from dotenv import load_dotenv
import requests
import logging
from telegram import Bot
from telegram.error import NetworkError, TelegramError

os.environ.pop('TELEGRAM_API_TOKEN', None)
os.environ.pop('TELEGRAM_CHAT_ID', None)
# Load the .env file
load_dotenv()
# Replace 'YOUR_API_TOKEN' with your actual API token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
print(CHAT_ID)
# Initialize the bot
bot = Bot(token=TELEGRAM_API_TOKEN)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def check_network():
    try:
        response = requests.get('https://api.telegram.org')
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        logger.error("No internet connection.")
        return False

def send_message():
    if check_network():
        try:
            bot.send_message(chat_id=CHAT_ID, text="Hello, this is a sent test message!")
            logger.info("Message sent")
        except NetworkError as e:
            logger.error(f"Network error: {e}")
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    send_message()