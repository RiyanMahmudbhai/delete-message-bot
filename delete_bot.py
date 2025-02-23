import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler
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

            # Check if the bot is an admin in the chat
            bot_member = bot.get_chat_member(chat_id, bot.id)

            # If the bot is not an admin or doesn't have delete permissions
            if bot_member.status not in ['administrator', 'creator']:
                update.message.reply_text("The bot is not an admin in this chat or doesn't have delete permissions.")
                return

            # Retrieve chat details (you may not be able to get the message history directly)
            # For this example, we just send a confirmation message
            update.message.reply_text("Bot has permissions to delete messages in this chat. Processing...")

            # Your message deletion logic would go here (requires additional setup)

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
