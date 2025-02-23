import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import BadRequest

# Setup logging to get info on errors and debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot's token
TOKEN = '7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI'

# Function to delete messages containing the specific text
def delete_messages(update: Update, context: CallbackContext):
    # Check if the user has provided a chat ID
    if len(context.args) == 1:
        chat_id = context.args[0]

        try:
            # Get the bot instance
            bot = update.message.bot

            # Check if the bot is an admin in the chat
            bot_member = bot.get_chat_member(chat_id, bot.id)

            # If the bot is not an admin or doesn't have delete permissions
            if bot_member.status not in ['administrator', 'creator']:
                update.message.reply_text("The bot is not an admin in this chat or doesn't have delete permissions.")
                return

            # Send a confirmation message to the user
            update.message.reply_text("Bot has permissions to delete messages in this chat. Processing...")

        except BadRequest as e:
            update.message.reply_text(f"Error: {e}")
    else:
        update.message.reply_text("Please provide the correct chat ID.")

# Function to monitor incoming messages and delete if matching text is found
def message_handler(update: Update, context: CallbackContext):
    message_text = update.message.text
    if "Leech Started" in message_text:
        try:
            # Delete the message if it contains "Leech Started"
            update.message.delete()
            logging.info(f"Deleted message: {update.message.message_id} from {update.message.chat_id}")
        except BadRequest as e:
            logging.error(f"Error deleting message: {e}")

# Start the bot and listen for commands
def start(update, context):
    update.message.reply_text("Welcome! Use /delete <chat_id> to delete filtered messages.")

# Main function to handle commands and updates
def main():
    updater = Updater(TOKEN, use_context=True)

    # Add command handler for the '/delete' command
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("delete", delete_messages))
    
    # Add message handler to delete "Leech Started" from incoming messages
    dp.add_handler(MessageHandler(filters.Filters.text & ~filters.Filters.command, message_handler))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
