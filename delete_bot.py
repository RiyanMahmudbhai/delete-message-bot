import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from telegram.error import BadRequest

# Setup logging to get info on errors and debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot's token
TOKEN = '7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI'

# Function to delete messages containing the specific text
def delete_messages(update, context):
    # Check if the user has provided a chat ID
    if len(context.args) == 1:
        chat_id = context.args[0]

        try:
            # Get the bot instance
            bot = Bot(token=TOKEN)

            # Getting the chat where the bot is looking for messages
            # Assuming the bot has permissions in the channel
            chat = bot.get_chat(chat_id)

            # Start scanning messages from the chat
            for message in chat.get_messages():
                if "Leech Started" in message.text:
                    bot.delete_message(chat_id=chat_id, message_id=message.message_id)

            # Send a confirmation message to the user
            update.message.reply_text("Action completed: Filtered messages deleted.")
        except BadRequest as e:
            update.message.reply_text(f"Error: {e}")
    else:
        update.message.reply_text("Please provide the correct chat ID.")

# Start the bot and listen for commands
def start(update, context):
    update.message.reply_text("Welcome! Use /delete <chat_id> to delete filtered messages.")

# Main function to handle commands and update the bot
def main():
    updater = Updater(TOKEN, use_context=True)

    # Add command handler for the '/delete' command
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("delete", delete_messages))
    dp.add_handler(CommandHandler("start", start))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
