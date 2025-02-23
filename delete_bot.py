import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler, filters
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

            # Fetch the recent messages from the chat (up to 100 messages)
            messages = bot.get_chat_history(chat_id=chat_id, limit=100)

            # Loop through the messages and delete those with the filter text
            deleted_count = 0
            for message in messages:
                if "Leech Started" in message.text:
                    bot.delete_message(chat_id=chat_id, message_id=message.message_id)
                    deleted_count += 1

            # Send a confirmation message to the user
            if deleted_count > 0:
                update.message.reply_text(f"Action completed: {deleted_count} messages deleted.")
            else:
                update.message.reply_text("No matching messages found.")

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
