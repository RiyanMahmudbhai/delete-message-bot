import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configure your bot token here
BOT_TOKEN = "7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI"

# Configure your channel mappings (source: destination)
CHANNEL_MAPPING = {
    -1002211636314: -1002492502401,  # Source Channel 1: Dest Channel 1
    -1001122334455: -1005566778899,  # Source Channel 2: Dest Channel 2
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    source_chat_id = message.chat_id
    
    # Check if message is from a mapped source channel
    if source_chat_id not in CHANNEL_MAPPING:
        return
    
    # Check if message contains a video file
    if message.document and message.document.mime_type.startswith('video/'):
        dest_chat_id = CHANNEL_MAPPING[source_chat_id]
        
        try:
            # Forward the message with the original filename
            await message.forward(dest_chat_id)
        except Exception as e:
            print(f"Error forwarding message: {e}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & filters.Document.VIDEO,
        handle_message
    ))
    app.run_polling()
