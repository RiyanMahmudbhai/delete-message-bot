import requests
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI"
CHANNEL_MAPPING = {
    -1002211636314: -1002492502401,
}

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    source_chat_id = message.chat_id

    if source_chat_id not in CHANNEL_MAPPING:
        return

    dest_chat_id = CHANNEL_MAPPING[source_chat_id]
    file_name = None
    file_id = None
    mime_type = None

    # Get file details based on message type
    if message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        mime_type = message.video.mime_type
    elif message.document and message.document.mime_type.startswith('video/'):
        file_id = message.document.file_id
        file_name = message.document.file_name
        mime_type = message.document.mime_type

    if not file_id or not file_name:
        return

    try:
        # Get file download URL from Telegram
        file = await context.bot.get_file(file_id)
        download_url = file.file_path

        # Stream file directly from Telegram's servers
        with requests.get(download_url, stream=True) as response:
            response.raise_for_status()
            
            # Create a file-like object from the stream
            file_stream = InputFile(
                response.raw,
                filename=file_name,
                mime_type=mime_type
            )

            # Send as document with original filename and mime type
            await context.bot.send_document(
                chat_id=dest_chat_id,
                document=file_stream,
                filename=file_name,
                caption=""
            )

    except Exception as e:
        print(f"Error processing video: {e}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & 
        (filters.VIDEO | (filters.Document.VIDEO)),
        handle_video
    ))
    app.run_polling()
