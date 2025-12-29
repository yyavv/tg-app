"""Message capture handlers for the Telegram bot."""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from db_handler import DatabaseHandler

logger = logging.getLogger(__name__)


class MessageCapture:
    """Handlers for capturing messages from groups."""
    
    @staticmethod
    async def handle_new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when the bot is added to a group."""
        if update.my_chat_member:
            chat = update.my_chat_member.chat
            new_status = update.my_chat_member.new_chat_member.status
            
            if new_status in ["member", "administrator"]:
                # Bot was added to a group
                DatabaseHandler.add_or_update_group(chat.id, chat.title)
                logger.info(f"Bot added to group: {chat.title} ({chat.id})")
    
    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Capture messages from groups."""
        message = update.message or update.edited_message
        
        if not message or not message.chat:
            return
        
        chat = message.chat
        
        # Only capture from groups and supergroups
        if chat.type not in ['group', 'supergroup']:
            return
        
        # Ensure group is in database
        DatabaseHandler.add_or_update_group(chat.id, chat.title)
        
        # Extract sender information
        sender = message.from_user
        sender_id = sender.id if sender else None
        sender_username = sender.username if sender else None
        sender_first_name = sender.first_name if sender else None
        sender_last_name = sender.last_name if sender else None
        
        # Extract topic information (for forum groups)
        topic_id = None
        topic_name = None
        if message.is_topic_message and message.message_thread_id:
            topic_id = message.message_thread_id
            
            # Try to get topic name from database first
            topic_name = DatabaseHandler.get_topic_name(chat.id, topic_id)
            
            # If not in database, try to fetch from Telegram
            if not topic_name:
                try:
                    # For forum topics, we need to get the topic info
                    # The topic name might be in the reply_to_message if it's a topic root
                    if message.reply_to_message and message.reply_to_message.forum_topic_created:
                        topic_name = message.reply_to_message.forum_topic_created.name
                    else:
                        # Try to get from chat
                        topic_name = f"Topic {topic_id}"  # Fallback
                        logger.debug(f"Using fallback topic name for topic {topic_id}")
                except Exception as e:
                    topic_name = f"Topic {topic_id}"
                    logger.warning(f"Could not fetch topic name: {e}")
            
            # Save/update topic in database
            DatabaseHandler.add_forum_topic(chat.id, topic_id, topic_name)
            logger.info(f"Processing message in topic '{topic_name}' ({topic_id}) in group '{chat.title}'")
        
        # Determine message type and extract content
        message_type = "text"
        text_content = None
        caption = None
        file_id = None
        
        if message.text:
            message_type = "text"
            text_content = message.text
        elif message.photo:
            message_type = "photo"
            file_id = message.photo[-1].file_id  # Get largest photo
            caption = message.caption
        elif message.video:
            message_type = "video"
            file_id = message.video.file_id
            caption = message.caption
        elif message.document:
            message_type = "document"
            file_id = message.document.file_id
            caption = message.caption
        elif message.audio:
            message_type = "audio"
            file_id = message.audio.file_id
            caption = message.caption
        elif message.voice:
            message_type = "voice"
            file_id = message.voice.file_id
            caption = message.caption
        elif message.video_note:
            message_type = "video_note"
            file_id = message.video_note.file_id
        elif message.sticker:
            message_type = "sticker"
            file_id = message.sticker.file_id
        elif message.animation:
            message_type = "animation"
            file_id = message.animation.file_id
            caption = message.caption
        elif message.location:
            message_type = "location"
            text_content = f"Location: {message.location.latitude}, {message.location.longitude}"
        elif message.poll:
            message_type = "poll"
            text_content = f"Poll: {message.poll.question}"
        else:
            message_type = "other"
        
        # Prepare message data
        message_data = {
            'group_id': chat.id,
            'group_name': chat.title,
            'message_id': message.message_id,
            'topic_id': topic_id,
            'topic_name': topic_name,
            'sender_id': sender_id,
            'sender_username': sender_username,
            'sender_first_name': sender_first_name,
            'sender_last_name': sender_last_name,
            'message_type': message_type,
            'text_content': text_content,
            'caption': caption,
            'file_id': file_id,
            'timestamp': datetime.fromtimestamp(message.date.timestamp())
        }
        
        # Save to database
        DatabaseHandler.save_message(message_data)
        
        logger.debug(f"Captured {message_type} message from {chat.title}")
    
    @staticmethod
    async def handle_forum_topic_created(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when a new forum topic is created."""
        message = update.message
        
        if not message or not message.forum_topic_created:
            return
        
        chat = message.chat
        topic = message.forum_topic_created
        topic_id = message.message_thread_id
        
        # Ensure group is in database
        DatabaseHandler.add_or_update_group(chat.id, chat.title)
        
        # Add topic to database
        DatabaseHandler.add_forum_topic(chat.id, topic_id, topic.name)
        logger.info(f"✨ New forum topic created: '{topic.name}' (ID: {topic_id}) in group '{chat.title}' (ID: {chat.id})")
    
    @staticmethod
    async def handle_forum_topic_edited(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when a forum topic is edited."""
        message = update.message
        
        if not message or not message.forum_topic_edited:
            return
        
        chat = message.chat
        topic = message.forum_topic_edited
        topic_id = message.message_thread_id
        
        # Update topic name in database
        DatabaseHandler.add_forum_topic(chat.id, topic_id, topic.name)
        logger.info(f"📝 Forum topic edited: '{topic.name}' (ID: {topic_id}) in group '{chat.title}' (ID: {chat.id})")
