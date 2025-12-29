"""Reinitialization logic for migrating messages between groups."""
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError, RetryAfter, BadRequest
from db_handler import DatabaseHandler
import config

logger = logging.getLogger(__name__)


class ReinitializationHandler:
    """Handle reinitialization of messages to a new group."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.errors = []
    
    async def reinitialize(self, source_group_id, target_group_id, progress_callback=None):
        """
        Reinitialize messages from source group to target group.
        
        Args:
            source_group_id: Source group ID
            target_group_id: Target group ID
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with statistics about the reinitialization
        """
        self.errors = []
        
        # Get source group info
        source_group = DatabaseHandler.get_group_by_id(source_group_id)
        if not source_group:
            raise ValueError(f"Source group {source_group_id} not found in database")
        
        # Get all messages from source group
        messages = DatabaseHandler.get_messages_for_group(source_group_id)
        total_messages = len(messages)
        
        if total_messages == 0:
            raise ValueError(f"No messages found for group {source_group_id}")
        
        logger.info(f"Starting reinitialization: {total_messages} messages from {source_group_id} to {target_group_id}")
        
        # Check if target is a forum group and get topics
        topics = DatabaseHandler.get_topics_for_group(source_group_id)
        topic_mapping = {}  # Map old topic IDs to new topic IDs
        topics_created = 0
        
        # Try to detect if target is a forum
        try:
            chat = await self.bot.get_chat(target_group_id)
            is_forum = chat.is_forum
        except Exception as e:
            logger.warning(f"Could not get chat info: {e}")
            is_forum = False
        
        # Create topics in target group if it's a forum
        if is_forum and topics:
            for topic in topics:
                try:
                    # Create forum topic in target group
                    forum_topic = await self.bot.create_forum_topic(
                        chat_id=target_group_id,
                        name=topic.topic_name
                    )
                    topic_mapping[topic.topic_id] = forum_topic.message_thread_id
                    topics_created += 1
                    logger.info(f"Created topic '{topic.topic_name}' with ID {forum_topic.message_thread_id}")
                except Exception as e:
                    logger.error(f"Failed to create topic '{topic.topic_name}': {e}")
        
        # Send messages to target group
        sent_count = 0
        failed_count = 0
        
        for i, message in enumerate(messages):
            try:
                # Determine message thread ID for forum groups
                message_thread_id = None
                if is_forum and message.topic_id and message.topic_id in topic_mapping:
                    message_thread_id = topic_mapping[message.topic_id]
                
                # Send message based on type
                await self._send_message(
                    target_group_id,
                    message,
                    message_thread_id
                )
                
                sent_count += 1
                
                # Progress update
                if progress_callback and (i + 1) % config.PROGRESS_UPDATE_INTERVAL == 0:
                    await progress_callback(i + 1, total_messages)
                
                # Rate limiting
                await asyncio.sleep(1 / config.MESSAGES_PER_SECOND)
                
            except RetryAfter as e:
                # Handle flood control
                wait_time = e.retry_after
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                # Retry this message
                try:
                    await self._send_message(target_group_id, message, message_thread_id)
                    sent_count += 1
                except Exception as retry_error:
                    failed_count += 1
                    self._log_error(message, retry_error)
            
            except Exception as e:
                failed_count += 1
                self._log_error(message, e)
        
        # Final progress update
        if progress_callback:
            await progress_callback(total_messages, total_messages)
        
        logger.info(f"Reinitialization complete: {sent_count} sent, {failed_count} failed")
        
        return {
            'total_messages': total_messages,
            'sent': sent_count,
            'failed': failed_count,
            'topics_created': topics_created,
            'errors': self.errors
        }
    
    async def _send_message(self, chat_id, message, message_thread_id=None):
        """Send a single message to the target group."""
        if message.message_type == "text":
            # Send text message
            text = message.text_content or ""
            if len(text) > config.MAX_MESSAGE_LENGTH:
                text = text[:config.MAX_MESSAGE_LENGTH - 3] + "..."
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "photo":
            # Send photo
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "video":
            # Send video
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_video(
                chat_id=chat_id,
                video=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "document":
            # Send document
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_document(
                chat_id=chat_id,
                document=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "audio":
            # Send audio
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_audio(
                chat_id=chat_id,
                audio=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "voice":
            # Send voice
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_voice(
                chat_id=chat_id,
                voice=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "video_note":
            # Send video note
            await self.bot.send_video_note(
                chat_id=chat_id,
                video_note=message.file_id,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "sticker":
            # Send sticker
            await self.bot.send_sticker(
                chat_id=chat_id,
                sticker=message.file_id,
                message_thread_id=message_thread_id
            )
        
        elif message.message_type == "animation":
            # Send animation
            caption = message.caption or ""
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            await self.bot.send_animation(
                chat_id=chat_id,
                animation=message.file_id,
                caption=caption,
                message_thread_id=message_thread_id
            )
        
        else:
            # For other types, send as text
            text = f"[{message.message_type.upper()}]"
            if message.text_content:
                text += f"\n{message.text_content}"
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                message_thread_id=message_thread_id
            )
    
    def _log_error(self, message, error):
        """Log an error during message sending."""
        error_info = {
            'message_id': message.message_id,
            'error': str(error)
        }
        self.errors.append(error_info)
        logger.error(f"Failed to send message {message.message_id}: {error}")
