"""Database operations for the Telegram bot."""
import logging
from datetime import datetime
from sqlalchemy import func
from database import (
    get_session, TelegramGroup, ForumTopic, CapturedMessage
)

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Handle all database operations."""
    
    @staticmethod
    def add_or_update_group(group_id, group_name):
        """Add or update a group in the database."""
        session = get_session()
        try:
            group = session.query(TelegramGroup).filter_by(group_id=group_id).first()
            if group:
                group.group_name = group_name
                group.updated_at = datetime.utcnow()
            else:
                group = TelegramGroup(group_id=group_id, group_name=group_name)
                session.add(group)
            session.commit()
            logger.info(f"Added/updated group: {group_name} ({group_id})")
        except Exception as e:
            logger.error(f"Error adding/updating group: {e}")
            session.rollback()
        finally:
            session.close()
    
    @staticmethod
    def add_forum_topic(group_id, topic_id, topic_name):
        """Add a forum topic to the database."""
        session = get_session()
        try:
            existing = session.query(ForumTopic).filter_by(
                group_id=group_id, topic_id=topic_id
            ).first()
            if existing:
                # Update topic name if it changed
                if existing.topic_name != topic_name:
                    existing.topic_name = topic_name
                    session.commit()
                    logger.info(f"Updated topic name: {topic_name} ({topic_id}) in group {group_id}")
            else:
                topic = ForumTopic(
                    group_id=group_id,
                    topic_id=topic_id,
                    topic_name=topic_name
                )
                session.add(topic)
                session.commit()
                logger.info(f"Added topic: {topic_name} ({topic_id}) in group {group_id}")
        except Exception as e:
            logger.error(f"Error adding forum topic: {e}")
            session.rollback()
        finally:
            session.close()
    
    @staticmethod
    def get_topic_name(group_id, topic_id):
        """Get topic name from database."""
        session = get_session()
        try:
            topic = session.query(ForumTopic).filter_by(
                group_id=group_id, topic_id=topic_id
            ).first()
            return topic.topic_name if topic else None
        finally:
            session.close()
    
    @staticmethod
    def save_message(message_data):
        """Save a captured message to the database."""
        session = get_session()
        try:
            message = CapturedMessage(**message_data)
            session.add(message)
            session.commit()
            logger.debug(f"Saved message {message_data['message_id']} from group {message_data['group_id']}")
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            session.rollback()
        finally:
            session.close()
    
    @staticmethod
    def get_all_groups():
        """Get all monitored groups with message counts."""
        session = get_session()
        try:
            groups = session.query(TelegramGroup).all()
            result = []
            for group in groups:
                message_count = session.query(CapturedMessage).filter_by(
                    group_id=group.group_id
                ).count()
                topic_count = session.query(ForumTopic).filter_by(
                    group_id=group.group_id
                ).count()
                if topic_count == 0:
                    topic_count = 1  # Default topic
                result.append({
                    'group_id': group.group_id,
                    'group_name': group.group_name,
                    'message_count': message_count,
                    'topic_count': topic_count
                })
            return result
        finally:
            session.close()
    
    @staticmethod
    def get_database_stats():
        """Get database statistics."""
        session = get_session()
        try:
            group_count = session.query(TelegramGroup).count()
            topic_count = session.query(ForumTopic).count()
            message_count = session.query(CapturedMessage).count()
            return {
                'groups': group_count,
                'topics': topic_count if topic_count > 0 else group_count,
                'messages': message_count
            }
        finally:
            session.close()
    
    @staticmethod
    def get_messages_for_group(group_id):
        """Get all messages for a specific group, ordered by timestamp."""
        session = get_session()
        try:
            messages = session.query(CapturedMessage).filter_by(
                group_id=group_id
            ).order_by(CapturedMessage.timestamp).all()
            return messages
        finally:
            session.close()
    
    @staticmethod
    def get_topics_for_group(group_id):
        """Get all topics for a specific group."""
        session = get_session()
        try:
            topics = session.query(ForumTopic).filter_by(
                group_id=group_id
            ).all()
            return topics
        finally:
            session.close()
    
    @staticmethod
    def get_group_by_id(group_id):
        """Get group information by ID."""
        session = get_session()
        try:
            return session.query(TelegramGroup).filter_by(group_id=group_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_topic_stats(group_id):
        """Get message count per topic for a group."""
        session = get_session()
        try:
            topics = session.query(ForumTopic).filter_by(group_id=group_id).all()
            result = []
            for topic in topics:
                count = session.query(CapturedMessage).filter_by(
                    group_id=group_id,
                    topic_id=topic.topic_id
                ).count()
                result.append({
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name,
                    'message_count': count
                })
            # Also get messages without topic (general messages)
            general_count = session.query(CapturedMessage).filter_by(
                group_id=group_id,
                topic_id=None
            ).count()
            if general_count > 0:
                result.insert(0, {
                    'topic_id': None,
                    'topic_name': 'General',
                    'message_count': general_count
                })
            return result
        finally:
            session.close()
    
    @staticmethod
    def get_recent_messages(limit=10, group_id=None, topic_id=None):
        """Get recent messages with optional filters."""
        session = get_session()
        try:
            query = session.query(CapturedMessage).order_by(
                CapturedMessage.timestamp.desc()
            )
            
            if group_id:
                query = query.filter_by(group_id=group_id)
            if topic_id is not None:
                query = query.filter_by(topic_id=topic_id)
            
            messages = query.limit(limit).all()
            return messages
        finally:
            session.close()
    
    @staticmethod
    def get_detailed_stats():
        """Get detailed statistics for all groups and topics."""
        session = get_session()
        try:
            # Total stats
            total_messages = session.query(CapturedMessage).count()
            total_groups = session.query(TelegramGroup).count()
            total_topics = session.query(ForumTopic).count()
            
            # Messages by type
            type_stats = session.query(
                CapturedMessage.message_type,
                func.count(CapturedMessage.id).label('count')
            ).group_by(CapturedMessage.message_type).all()
            
            # Most active groups
            active_groups = session.query(
                CapturedMessage.group_id,
                CapturedMessage.group_name,
                func.count(CapturedMessage.id).label('count')
            ).group_by(
                CapturedMessage.group_id,
                CapturedMessage.group_name
            ).order_by(func.count(CapturedMessage.id).desc()).limit(5).all()
            
            # Most active topics
            active_topics = session.query(
                CapturedMessage.topic_name,
                CapturedMessage.group_name,
                func.count(CapturedMessage.id).label('count')
            ).filter(
                CapturedMessage.topic_id.isnot(None)
            ).group_by(
                CapturedMessage.topic_name,
                CapturedMessage.group_name
            ).order_by(func.count(CapturedMessage.id).desc()).limit(5).all()
            
            return {
                'total_messages': total_messages,
                'total_groups': total_groups,
                'total_topics': total_topics,
                'type_stats': type_stats,
                'active_groups': active_groups,
                'active_topics': active_topics
            }
        finally:
            session.close()
