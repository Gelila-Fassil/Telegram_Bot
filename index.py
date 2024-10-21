import os
import json
import logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import os
from os.path import join, exists
import re

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the random numbers from the JSON file
with open('numbers.json', 'r') as f:
    random_numbers = set(json.load(f))

music_dir = join(os.path.dirname(__file__), 'music')

async def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message when the user types /start."""
    await update.message.reply_text("Welcome! Enter your key number to get your music.")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handles user messages and processes the music download logic."""
    user_message = update.message.text.strip()
    chat_id = update.message.chat_id

    # Ignore if the user types /start
    if user_message == '/start':
        return

    # Check if the message is a valid number
    if re.match(r'^\d+$', user_message):
        user_number = int(user_message)

        # Check if the number exists in the random number set
        if user_number in random_numbers:
            random_numbers.remove(user_number)  # Remove used number
            await update.message.reply_text("Thank you for your purchase! Here are the available tracks:")

            if not exists(music_dir):
                await update.message.reply_text(f"Directory '{music_dir}' not found!")
                return

            # List available tracks from the 'music' directory
            music_files = [file for file in os.listdir(music_dir) if file.endswith('.mp3')]

            if not music_files:
                await update.message.reply_text(f"No music files found in '{music_dir}'.")
                return

            # Create buttons for each track
            keyboard = [[InlineKeyboardButton(track, callback_data=track)] for track in music_files]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send track selection options
            await update.message.reply_text("Choose a track to download:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Sorry, the number you entered has already been used or is invalid. Please try another.")
    else:
        await update.message.reply_text("Please enter a valid number.")

async def handle_track_selection(update: Update, context: CallbackContext) -> None:
    """Handles track selection and sends the selected audio file."""
    query = update.callback_query
    await query.answer()

    track_name = query.data
    file_path = join(music_dir, track_name)

    if exists(file_path):
        await query.message.reply_audio(audio=open(file_path, 'rb'))
        await query.answer(text="Track is being sent!")
    else:
        await query.answer(text=f"Sorry, the track '{track_name}' was not found.", show_alert=True)

async def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    # Create the Application object (replaces Updater in v20+)
    application = Application.builder().token(TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Message handler for all other messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback handler for track selection
    application.add_handler(CallbackQueryHandler(handle_track_selection))

    # Log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
