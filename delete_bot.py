from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI"
CHANNEL_MAPPING = {
    -1002211636314: -1002492502401,
    -1001122334455: -1005566778899,
}

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    source_chat_id = message.chat_id

    if source_chat_id not in CHANNEL_MAPPING:
        return

    dest_chat_id = CHANNEL_MAPPING[source_chat_id]
    
    try:
        # Handle native Telegram videos
        if message.video:
            await context.bot.send_video(
                chat_id=dest_chat_id,
                video=message.video.file_id,
                filename=message.video.file_name or f"video_{message.video.file_unique_id}.mp4",
                caption=""
            )
        
        # Handle video documents
        elif message.document and message.document.mime_type.startswith('video/'):
            await context.bot.send_document(
                chat_id=dest_chat_id,
                document=message.document.file_id,
                filename=message.document.file_name,
                caption=""
            )
            
    except Exception as e:
        print(f"Error forwarding video: {e}")

if __name__ == "__main__":
    print("Starting video forwarding bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & 
        (filters.VIDEO | (filters.Document.VIDEO)),
        handle_video
    ))
    
    app.run_polling()
