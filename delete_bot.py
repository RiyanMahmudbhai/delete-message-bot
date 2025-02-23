import os
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
    video_file = None
    file_name = None

    # Handle different video types
    if message.video:
        video_file = await message.video.get_file()
        file_name = message.video.file_name or f"video_{message.video.file_id.split('-')[0]}.mp4"
    elif message.document and message.document.mime_type.startswith('video/'):
        video_file = await message.document.get_file()
        file_name = message.document.file_name

    if video_file and file_name:
        try:
            # Download the video
            download_path = await video_file.download_to_drive(custom_path=file_name)
            
            # Send as new message with original filename
            if message.document:
                await context.bot.send_document(
                    chat_id=dest_chat_id,
                    document=download_path,
                    filename=file_name
                )
            else:
                await context.bot.send_video(
                    chat_id=dest_chat_id,
                    video=download_path,
                    filename=file_name
                )
            
            # Clean up downloaded file
            os.remove(download_path)
            
        except Exception as e:
            print(f"Error processing video: {e}")
            if download_path and os.path.exists(download_path):
                os.remove(download_path)

if __name__ == "__main__":
    print("Starting video forwarding bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handle both video files and video documents
    app.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & 
        (filters.VIDEO | (filters.Document.VIDEO)),
        handle_video
    ))
    
    app.run_polling()
