"""Main bot file - Telegram Message Capture Bot."""
import logging
import os
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


def main():
    """Start the bot."""
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
    
    # Start the bot
    logger.info("Starting bot...")
    logger.info(f"Admin IDs: {config.ADMIN_IDS}")
    application.run_polling(allowed_updates=["message", "edited_message", "my_chat_member"])


if __name__ == '__main__':
    main()
