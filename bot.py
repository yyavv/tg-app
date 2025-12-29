"""Main bot file - Telegram Message Capture Bot (Webhook Mode for Vercel)."""
import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters
)
import config
from database import init_db
from message_handlers import MessageCapture
from admin_commands import AdminCommands
from reinit_command import reinitialize_command

# Configure logging (Vercel only supports console/stdout)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console only for Vercel
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize database
logger.info("Initializing database...")
init_db()

# Create application
logger.info("Creating bot application...")
application = Application.builder().token(config.BOT_TOKEN).build()

# Register command handlers
application.add_handler(CommandHandler("start", AdminCommands.start))
application.add_handler(CommandHandler("help", AdminCommands.help_command))
application.add_handler(CommandHandler("status", AdminCommands.status))
application.add_handler(CommandHandler("list_groups", AdminCommands.list_groups))
application.add_handler(CommandHandler("list_topics", AdminCommands.list_topics))
application.add_handler(CommandHandler("recent", AdminCommands.recent))
application.add_handler(CommandHandler("stats", AdminCommands.stats))
application.add_handler(CommandHandler("reinitialize", reinitialize_command))

# Register chat member handler (for when bot is added to groups)
application.add_handler(
    ChatMemberHandler(
        MessageCapture.handle_new_chat_member,
        ChatMemberHandler.MY_CHAT_MEMBER
    )
)

# Register message handlers for capturing
application.add_handler(
    MessageHandler(
        filters.ChatType.GROUPS & ~filters.COMMAND,
        MessageCapture.handle_message
    )
)

# Handle edited messages
application.add_handler(
    MessageHandler(
        filters.ChatType.GROUPS & filters.UpdateType.EDITED_MESSAGE,
        MessageCapture.handle_message
    )
)

# Handle forum topic creation
application.add_handler(
    MessageHandler(
        filters.StatusUpdate.FORUM_TOPIC_CREATED,
        MessageCapture.handle_forum_topic_created
    )
)

# Handle forum topic edited
application.add_handler(
    MessageHandler(
        filters.StatusUpdate.FORUM_TOPIC_EDITED,
        MessageCapture.handle_forum_topic_edited
    )
)

logger.info("Bot handlers registered")
logger.info(f"Admin IDs: {config.ADMIN_IDS}")


@app.route('/')
def index():
    """Health check endpoint."""
    return 'Telegram Bot is running!', 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram."""
    try:
        # Verify secret token if configured
        if config.WEBHOOK_SECRET:
            secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            if secret_header != config.WEBHOOK_SECRET:
                logger.warning(f"Invalid webhook secret token from {request.remote_addr}")
                return 'Unauthorized', 403
        
        # Get the update from the request
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Initialize, process, and shutdown in one async block
        async def process():
            await application.initialize()
            try:
                await application.process_update(update)
            finally:
                await application.shutdown()
        
        asyncio.run(process())
        
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return 'Error', 500


@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """Set the webhook URL for the bot."""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        return 'WEBHOOK_URL environment variable not set', 400
    
    try:
        # Set webhook with secret token if configured
        webhook_params = {'url': f"{webhook_url}/webhook"}
        if config.WEBHOOK_SECRET:
            webhook_params['secret_token'] = config.WEBHOOK_SECRET
            logger.info("Setting webhook with secret token")
        
        # Run async operation
        asyncio.run(application.bot.set_webhook(**webhook_params))
        return f'Webhook set to {webhook_url}/webhook (secured: {bool(config.WEBHOOK_SECRET)})', 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}", exc_info=True)
        return f'Error: {e}', 500


# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5000)
