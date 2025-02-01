import logging
import os
import tracemalloc  # Add this import

from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters

logger = logging.getLogger(__name__)

# Store bot screaming status
screaming = False

# Pre-assign menu text
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

# Pre-assign button text
NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

# Build keyboards
FIRST_MENU_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)
]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])

# Pre-assign new menu text
NEW_MENU = "<b>New Menu</b>\n\nChoose an option below:"

# Pre-assign new button text
OPTION_ONE_BUTTON = "Option 1"
OPTION_TWO_BUTTON = "Option 2"

# Build new keyboard
NEW_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(OPTION_ONE_BUTTON, callback_data=OPTION_ONE_BUTTON)],
    [InlineKeyboardButton(OPTION_TWO_BUTTON, callback_data=OPTION_TWO_BUTTON)]
])


async def echo(update: Update, context: CallbackContext) -> None:
    """
    This function would be added to the dispatcher as a handler for messages coming from the Bot API
    """

    # Print to console
    print(f'{update.message.from_user.first_name} wrote {update.message.text}')

    if screaming and update.message.text:
        await context.bot.send_message(
            update.message.chat_id,
            update.message.text.upper(),
            # To preserve the markdown, we attach entities (bold, italic...)
            entities=update.message.entities
        )
    else:
        # This is equivalent to forwarding, without the sender's name
        await update.message.copy(update.message.chat_id)


async def scream(update: Update, context: CallbackContext) -> None:
    """
    This function handles the /scream command
    """

    global screaming
    screaming = True


async def whisper(update: Update, context: CallbackContext) -> None:
    """
    This function handles /whisper command
    """

    global screaming
    screaming = False


async def menu(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    await context.bot.send_message(
        update.message.from_user.id,
        FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )

async def button_tap(update: Update, context: CallbackContext) -> None:
    """
    This handler processes the inline buttons on the menu
    """

    data = update.callback_query.data
    text = ''
    markup = None

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    # Close the query to end the client-side loading animation
    await update.callback_query.answer()

    # Update message content with corresponding menu section
    await update.callback_query.message.edit_text(
        text,
        ParseMode.HTML,
        reply_markup=markup
    )


async def new_menu(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a new menu with the inline buttons we pre-assigned above
    """
    await context.bot.send_message(
        update.message.from_user.id,
        NEW_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=NEW_MENU_MARKUP
    )


async def new_button_tap(update: Update, context: CallbackContext) -> None:
    """
    This handler processes the inline buttons on the new menu
    """
    data = update.callback_query.data
    response_text = ''

    if data == OPTION_ONE_BUTTON:
        response_text = "You selected Option 1."
    elif data == OPTION_TWO_BUTTON:
        response_text = "You selected Option 2."

    # Close the query to end the client-side loading animation
    await update.callback_query.answer()

    # Send response message
    await context.bot.send_message(
        update.callback_query.message.chat_id,
        response_text
    )


async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to notify the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    update.message.reply_text('An error occurred, please try again later.')


def main() -> None:
    tracemalloc.start()  # Enable tracemalloc

    TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("scream", scream))
    application.add_handler(CommandHandler("whisper", whisper))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("newmenu", new_menu))  # Register new menu command

    # Register handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_tap))
    application.add_handler(CallbackQueryHandler(new_button_tap, pattern=f"^{OPTION_ONE_BUTTON}$|^{OPTION_TWO_BUTTON}$"))  # Register new button tap handler

    # Echo any message that is not a command
    application.add_handler(MessageHandler(~filters.COMMAND, echo))

    # Register the error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()

    # Run the bot until you press Ctrl-C
    application.idle()


if __name__ == '__main__':
    main()