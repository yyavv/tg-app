"""Main bot file - Telegram Message Capture Bot (Webhook Mode for Vercel)."""
import logging
import os
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

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging with both file and console output
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
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
async def webhook():
    """Handle incoming webhook updates from Telegram."""
    try:
        # Get the update from the request
        update = Update.de_json(request.get_json(force=True), application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return 'Error', 500


@app.route('/set-webhook', methods=['GET'])
async def set_webhook():
    """Set the webhook URL for the bot."""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        return 'WEBHOOK_URL environment variable not set', 400
    
    try:
        await application.bot.set_webhook(url=f"{webhook_url}/webhook")
        return f'Webhook set to {webhook_url}/webhook', 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return f'Error: {e}', 500


# Vercel serverless function handler
async def handler(request):
    """Handler for Vercel serverless functions."""
    return app(request.environ, lambda *args: None)
