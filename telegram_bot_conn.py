import logging
import os
import tracemalloc
import asyncio
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
from script_selenium import ElementFinderSeleniumBot

# Load the .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_API_TOKEN' with your actual API token
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

bot = ElementFinderSeleniumBot(USER, PASSWORD)

VALID_SHIPS = ['MSC World Europa', 'MSC Seaside', 'MSC Meraviglia']  # Add your valid ship names here
VALID_PORT_DEPARTURE = ['Genoa', 'Barcelona', 'Miami']  # Add your valid port of departure names here
chosen_ship = None  # Global variable to store the chosen ship
chosen_port = None  # Global variable to store the chosen port

async def send_screenshot(update: Update, context: CallbackContext) -> None:
    """
    This function has the purpose of taking a screenshot of the specified ship
    """
    try:
        # Determine the chat_id and user_id based on whether the update is a message or a callback query
        if update.message:
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            user_first_name = update.message.from_user.first_name
            user_text = update.message.text
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
            user_id = update.callback_query.from_user.id
            user_first_name = update.callback_query.from_user.first_name
            user_text = update.callback_query.data
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Something went wrong. Please try again later.")
            return

        logger.info(f'{user_first_name} wrote {user_text}')
        
        if chosen_ship and chosen_port:
            ship_name = chosen_ship
            port_of_departure = chosen_port
        else:
            if len(context.args) < 2:
                await context.bot.send_message(chat_id=chat_id, text="Please provide a ship name and a port of departure separated by a hyphen (-).")
                return

            ship_name, port_of_departure = context.args[0].split('-')

            logger.debug(f"Read from user ==> Ship name: {ship_name} and Port of Departure: {port_of_departure}")

            if ship_name not in VALID_SHIPS:
                error_message = (
                    f"Invalid ship name: {ship_name}\n"
                    "Valid ship names are:\n" +
                    "\n".join(VALID_SHIPS)
                )
                await context.bot.send_message(chat_id=chat_id, text=error_message)
                return

            if port_of_departure not in VALID_PORT_DEPARTURE:
                error_message = (
                    f"Invalid port of departure: {port_of_departure}\n"
                    "Valid ports of departure are:\n" +
                    "\n".join(VALID_PORT_DEPARTURE)
                )
                await context.bot.send_message(chat_id=chat_id, text=error_message)
                return

        WelcomeMsg = (
            "<b>Welcome to the Cruises Finder Bot!</b> 🚢\n\n"
            "<b>Wait while the system generates a simulation for you...</b>\n\n"
            f"<b>I'm looking for a cruise with Ship Name:</b> {ship_name} and <b>Port of Departure:</b> {port_of_departure}\n\n"
            "This process may take a few seconds, please be patient. 🕒"
        )

        await context.bot.send_message(
            user_id,
            text=WelcomeMsg,
            parse_mode=ParseMode.HTML
        )

        await bot.run_script_on_selenium(ship_name, port_of_departure)

        # Get the screenshot path
        screenshot_path = bot.get_screenshot_path()

        # Send the screenshot to the Telegram bot
        with open(screenshot_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Something went wrong. Please try again later.")

async def show_help(update: Update, context: CallbackContext) -> None:
    try:
        help_text = (
            "Available commands:\n"
            "<b>/screenshot [ship_name-port_of_departure] - Take a screenshot of the specified ship and port of departure, and send it to the chat</b>\n"
            "<i> Example: /screenshot MSC World Europa-Genoa</i>\n\n"
            "keep in mind that if you don't provide the ship name and port of departure, you will be prompted to select them from a menu.\n\n"
            "<b>/help - Show this help message</b>\n"
            "<b>/validships - Show the valid ship names</b>\n"
            "<b>/validports - Show the valid port of departure names</b>\n"
            "<b>/select_ship - Show a menu with buttons for select a valid ship</b>\n"
            "<b>/select_cruise_departure - Show a menu with buttons for select a valid port of departure</b>\n"
        )
        await context.bot.send_message(
            update.message.from_user.id,
            text=help_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

async def show_valid_ships(update: Update, context: CallbackContext) -> None:
    try:
        valid_ships_text = "Valid ship names are:\n" + "\n".join(VALID_SHIPS)
        await context.bot.send_message(chat_id=update.message.chat_id, text=valid_ships_text)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

async def show_valid_ports(update: Update, context: CallbackContext) -> None:
    try:
        valid_ports_text = "Valid ports of departure are:\n" + "\n".join(VALID_PORT_DEPARTURE)
        await context.bot.send_message(chat_id=update.message.chat_id, text=valid_ports_text)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

async def select_ship(update: Update, context: CallbackContext) -> None:
    try:
        ship_keyboard = [[InlineKeyboardButton(ship, callback_data=f"ship:{ship}")] for ship in VALID_SHIPS]
        reply_markup = InlineKeyboardMarkup(ship_keyboard)
        await context.bot.send_message(chat_id=update.message.chat_id, text="Choose a ship:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

async def select_cruise_departure(update: Update, context: CallbackContext) -> None:
    try:
        port_keyboard = [[InlineKeyboardButton(port, callback_data=f"port:{port}")] for port in VALID_PORT_DEPARTURE]
        reply_markup = InlineKeyboardMarkup(port_keyboard)
        await context.bot.send_message(chat_id=update.message.chat_id, text="Choose a port of departure:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

async def ship_button_tap(update: Update, context: CallbackContext) -> None:
    try:
        global chosen_ship
        query = update.callback_query
        chosen_ship = query.data.split(":")[1]
        await query.answer()
        await query.edit_message_text(text=f"Selected ship: {chosen_ship}")
        if chosen_ship and chosen_port:
            await send_screenshot(update, context)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=query.message.chat_id, text="Something went wrong. Please try again later.")

async def port_button_tap(update: Update, context: CallbackContext) -> None:
    try:
        global chosen_port
        query = update.callback_query
        chosen_port = query.data.split(":")[1]
        await query.answer()
        await query.edit_message_text(text=f"Selected port: {chosen_port}")
        if chosen_ship and chosen_port:
            await send_screenshot(update, context)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=query.message.chat_id, text="Something went wrong. Please try again later.")

async def invalid_command(update: Update, context: CallbackContext) -> None:
    try:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Invalid command. Please choose a valid option from the menu.")
        await show_help(update, context)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id=update.message.chat_id, text="Something went wrong. Please try again later.")

def main() -> None:
    tracemalloc.start()  # Enable tracemalloc
    application = Application.builder().token(API_TOKEN).build()
    # Register the send_screenshot command
    application.add_handler(CommandHandler("screenshot", send_screenshot))
    # Register the help command
    application.add_handler(CommandHandler("help", show_help))
    # Register the valid ships command
    application.add_handler(CommandHandler("validships", show_valid_ships))
    # Register the valid ports command
    application.add_handler(CommandHandler("validports", show_valid_ports))
    # Register the select ship command
    application.add_handler(CommandHandler("select_ship", select_ship))
    # Register the select cruise departure command
    application.add_handler(CommandHandler("select_cruise_departure", select_cruise_departure))
    # Register the ship button tap handler
    application.add_handler(CallbackQueryHandler(ship_button_tap, pattern="^ship:"))
    # Register the port button tap handler
    application.add_handler(CallbackQueryHandler(port_button_tap, pattern="^port:"))
    # Register the invalid command handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, invalid_command))
    # Start the Bot
    application.run_polling()
    # Run the bot until you press Ctrl-C
    application.idle()

if __name__ == '__main__':
    main()