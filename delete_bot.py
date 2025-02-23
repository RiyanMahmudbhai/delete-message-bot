from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = '7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI'
TARGET_TEXT = "➲ Leech Started :"

async def delete_all_filtered_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Validate command format
        if not context.args:
            await update.message.reply_text("⚠️ Usage: /delete <channel_chat_id>")
            return

        # Convert chat ID to integer
        try:
            chat_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid chat ID! Must be numeric (e.g., -1001234567890)")
            return

        # Verify user is channel admin
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            if update.effective_user.id not in [admin.user.id for admin in admins]:
                await update.message.reply_text("⛔️ You must be admin in the target channel!")
                return
        except Exception as e:
            await update.message.reply_text(f"❌ Admin check failed: {str(e)}")
            return

        # Start cleanup process
        await update.message.reply_text("🔍 Scanning messages...")
        deleted_count = 0
        
        # Proper message iteration with modern API
        async for message in context.bot.get_chat_history(chat_id=chat_id):
            if message.text and TARGET_TEXT in message.text:
                try:
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=message.message_id
                    )
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting message {message.message_id}: {e}")

        # Send completion report
        await update.message.reply_text(
            f"✅ Cleanup complete!\n"
            f"🗑 Deleted {deleted_count} messages containing '{TARGET_TEXT}'"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Critical Error: {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("delete", delete_all_filtered_messages))
    print("Bot running in manual cleanup mode...")
    application.run_polling()

if __name__ == "__main__":
    main()