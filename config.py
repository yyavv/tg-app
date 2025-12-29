"""Configuration management for the Telegram bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

# Admin Configuration
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip()]

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Rate Limiting Configuration
MESSAGES_PER_SECOND = 20
FLOOD_WAIT_TIME = 30  # seconds

# Message Processing
MAX_MESSAGE_LENGTH = 4096
PROGRESS_UPDATE_INTERVAL = 100  # messages
