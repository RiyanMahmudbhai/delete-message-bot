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

            # Retrieve chat details
            chat = bot.get_chat(chat_id)

            # Check if the bot is an admin with permissions to delete messages
            if not chat.is_member or not chat.can_delete_messages:
                update.message.reply_text("The bot does not have permission to delete messages in this chat.")
                return

            # Get messages from the chat (this is a placeholder, as direct message access may not be allowed)
            # You may have to implement an external API or polling mechanism if you need to scan a large amount
            # of messages over time.

            # Send a completion message (since direct message retrieval might not be possible)
            update.message.reply_text("Message deletion is not possible due to API limitations.")
            
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
