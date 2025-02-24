import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, ChatWriteForbidden, FloodWait

# Configuration Class
class Config:
    BOT_TOKEN = "7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI"
    API_ID = "25902474"
    API_HASH = "e0613c7a7b94e0025a20f5cf7bc69eee"
    CHANNEL = [
        "-2222222222222:-1111111111111",
        "-1002211636314:-1002492502401",
        "-1002386644256:-1002484982348"
        "-1002418710282:-1002292610792"
    ]  # Add multiple mappings as needed

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MediaForwardBot(Client, Config):
    def __init__(self):
        super().__init__(
            name="MediaForwardBot",
            bot_token=self.BOT_TOKEN,
            api_id=self.API_ID,
            api_hash=self.API_HASH,
            workers=5  # Reduced workers for better rate limiting
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logger.info(f"Bot started as {me.first_name} (@{me.username})")

    async def stop(self):
        await super().stop()
        logger.info("Bot stopped.")

# Initialize Bot
bot = MediaForwardBot()

@bot.on_message(filters.channel & (filters.video | filters.document))
async def forward_media(client, message):
    try:
        # Check if the message contains a video or document
        if not (message.video or message.document):
            return

        # Validate media type for documents
        if message.document and not message.document.mime_type.startswith('video/'):
            return

        for mapping in client.CHANNEL:  # Use instance configuration
            try:
                source, destination = mapping.split(":")
            except ValueError:
                logger.error(f"Invalid mapping format: {mapping}. Use 'source:destination'")
                continue

            if str(message.chat.id) != source:
                continue

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await asyncio.sleep(0.5)  # Throttle between forwards
                    await message.copy(int(destination))
                    logger.info(f"Forwarded content from {source} to {destination}")
                    break  # Success - exit retry loop
                except FloodWait as e:
                    wait_time = e.value + 5  # Add buffer time
                    logger.warning(f"FloodWait: Waiting {wait_time}s (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                except ChatWriteForbidden:
                    logger.error(f"Bot lacks permissions in destination: {destination}")
                    break  # Non-retryable error
                except PeerIdInvalid:
                    logger.error(f"Invalid destination ID: {destination}")
                    break  # Non-retryable error
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts")
                    await asyncio.sleep(5)  # Wait before retry

    except Exception as e:
        logger.error(f"Critical error in handler: {str(e)}", exc_info=True)

if __name__ == "__main__":
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal startup error: {str(e)}", exc_info=True)
