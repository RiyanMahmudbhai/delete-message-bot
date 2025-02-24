import logging
import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.errors import (
    PeerIdInvalid,
    ChatWriteForbidden,
    FloodWait,
    UserNotParticipant,
    ChannelPrivate
)
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration Class
class Config:
    BOT_TOKEN = "7767525032:AAFkWn_ncuwdgHoIkJizAJowt2MzpWXgVnI"
    API_ID = "25902474"
    API_HASH = "e0613c7a7b94e0025a20f5cf7bc69eee"
    MONGODB_URI = "mongodb+srv://rusoxyny:rusoxyny@cluster0.e4uj5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

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
            workers=5
        )
        self.mongo_client = None
        self.db = None
        self.mappings = None

    async def start(self):
        await super().start()
        self.mongo_client = AsyncIOMotorClient(self.MONGODB_URI)
        self.db = self.mongo_client['forward_bot']
        self.mappings = self.db['mappings']
        me = await self.get_me()
        logger.info(f"Bot started as {me.first_name} (@{me.username})")

    async def stop(self):
        await super().stop()
        logger.info("Bot stopped.")

# Initialize Bot
bot = MediaForwardBot()

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply(
        "🤖 **Media Forwarding Bot**\n\n"
        "I can forward media from channels you specify\! Here's how:\n"
        "1\. Add me as admin in both source and destination channels\n"
        "2\. Use /set to create mappings\n"
        "3\. I'll auto\-forward new media\n\n"
        "**Commands:**\n"
        "/set \[source\] \[dest\] \- Create mapping\n"
        "/list \- Show all mappings\n"
        "/delete \[source\] \[dest\] \- Remove mapping\n"
        "/getid \- Get channel ID by forwarding message\n"
        "/help \- Show help",
        parse_mode="markdownv2"
    )

@bot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    await message.reply(
        "🆘 **Help**\n\n"
        "**Available Commands:**\n"
        "/set \- Create source\-destination mapping\n"
        "/list \- Show all active mappings\n"
        "/delete \- Remove a mapping\n"
        "/getid \- Get channel ID by forwarding message\n\n"
        "**Usage:**\n"
        "1\. Forward any channel message to me and use /getid\n"
        "2\. Use /set with the obtained IDs\n"
        "3\. Make sure I'm admin in both channels\!",
        parse_mode="markdownv2"
    )
@bot.on_message(filters.command("getid") & filters.private)
async def get_id_command(client, message):
    if not message.forward_from_chat:
        return await message.reply("Forward a channel message to get its ID!")
    
    chat = message.forward_from_chat
    await message.reply(
        f"**Channel ID:** `{chat.id}`\n"
        f"**Name:** {chat.title}\n"
        f"**Type:** {chat.type}",
        parse_mode="markdownv2"
    )

@bot.on_message(filters.command("set") & filters.private)
async def set_mapping(client, message):
    try:
        args = message.text.split()
        if len(args) != 3:
            return await message.reply("❌ **Usage:** /set [source_id] [dest_id]")

        _, source, dest = args
        
        try:
            source = int(source)
            dest = int(dest)
        except ValueError:
            return await message.reply("❌ IDs must be integers!")

        # Verify user permissions
        try:
            user = message.from_user
            for chat_id in [source, dest]:
                member = await client.get_chat_member(chat_id, user.id)
                if member.status not in ["administrator", "creator"]:
                    return await message.reply(f"❌ You're not admin in {chat_id}!")
        except (PeerIdInvalid, ChannelPrivate):
            return await message.reply("❌ Invalid channel ID or I'm not in that channel!")
        except UserNotParticipant:
            return await message.reply("❌ You're not in that channel!")

        # Verify bot permissions
        bot_user = await client.get_me()
        for chat_id, purpose in [(source, "source"), (dest, "destination")]:
            try:
                member = await client.get_chat_member(chat_id, bot_user.id)
                if not member.can_post_messages:
                    return await message.reply(f"❌ I need post permissions in {purpose} channel!")
            except PeerIdInvalid:
                return await message.reply(f"❌ I'm not in the {purpose} channel!")

        # Check existing mapping
        existing = await client.mappings.find_one({"source": source, "destination": dest})
        if existing:
            return await message.reply("⚠️ This mapping already exists!")

        # Insert new mapping
        await client.mappings.insert_one({
            "source": source,
            "destination": dest,
            "added_by": user.id,
            "date_added": datetime.datetime.utcnow()
        })
        
        await message.reply(f"✅ Mapping created!\n{source} → {dest}")

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        logger.error(f"Set mapping error: {str(e)}", exc_info=True)

@bot.on_message(filters.command("list") & filters.private)
async def list_mappings(client, message):
    try:
        mappings = []
        async for doc in client.mappings.find({}):
            mappings.append(
                f"• `{doc['source']}` → `{doc['destination']}` "
                f"(by <a href='tg://user?id={doc['added_by']}'>{doc['added_by']}</a>)"
            )
        
        if not mappings:
            return await message.reply("ℹ️ No active mappings!")
        
        await message.reply(
            "📋 **Active Mappings:**\n\n" + "\n".join(mappings),
            parse_mode="html",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        logger.error(f"List mappings error: {str(e)}", exc_info=True)

@bot.on_message(filters.command("delete") & filters.private)
async def delete_mapping(client, message):
    try:
        args = message.text.split()
        if len(args) != 3:
            return await message.reply("❌ **Usage:** /delete [source_id] [dest_id]")

        _, source, dest = args
        
        try:
            source = int(source)
            dest = int(dest)
        except ValueError:
            return await message.reply("❌ IDs must be integers!")

        # Verify user permissions
        user = message.from_user
        try:
            member = await client.get_chat_member(source, user.id)
            if member.status not in ["administrator", "creator"]:
                return await message.reply("❌ You're not admin in the source channel!")
        except (PeerIdInvalid, ChannelPrivate):
            return await message.reply("❌ Invalid source channel!")

        # Delete mapping
        result = await client.mappings.delete_one({"source": source, "destination": dest})
        
        if result.deleted_count > 0:
            await message.reply(f"✅ Mapping deleted!\n{source} → {dest}")
        else:
            await message.reply("ℹ️ No such mapping found!")

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
        logger.error(f"Delete mapping error: {str(e)}", exc_info=True)

@bot.on_message(filters.channel & (filters.video | filters.document))
async def forward_media(client, message):
    try:
        if message.document and not message.document.mime_type.startswith('video/'):
            return

        source_id = message.chat.id
        mappings = await client.mappings.find({"source": source_id}).to_list(None)

        for mapping in mappings:
            try:
                await message.copy(mapping['destination'])
                logger.info(f"Forwarded {message.id} to {mapping['destination']}")
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value + 5)
            except (ChatWriteForbidden, PeerIdInvalid):
                logger.warning(f"Can't write to {mapping['destination']}")
            except Exception as e:
                logger.error(f"Forward error: {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Media handler error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
