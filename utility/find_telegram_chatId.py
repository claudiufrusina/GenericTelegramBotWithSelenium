import os
from dotenv import load_dotenv
from telegram import Update
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters

os.environ.pop('TELEGRAM_API_TOKEN', None)
# Load the .env file
load_dotenv()


API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    print(f"Chat ID: {chat_id}")

def main() -> None:
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()
    application.idle()

if __name__ == '__main__':
    main()