"""Database models for storing Telegram messages."""
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import config

Base = declarative_base()

# Get database URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{config.DATABASE_PATH}')

# Fix for Vercel Postgres (uses postgres:// instead of postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


class TelegramGroup(Base):
    """Model for storing Telegram groups."""
    __tablename__ = 'telegram_groups'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, unique=True, nullable=False, index=True)
    group_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ForumTopic(Base):
    """Model for storing forum topics."""
    __tablename__ = 'forum_topics'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, nullable=False, index=True)
    topic_id = Column(Integer, nullable=False)
    topic_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class CapturedMessage(Base):
    """Model for storing captured messages."""
    __tablename__ = 'captured_messages'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(BigInteger, nullable=False, index=True)
    group_name = Column(String(255))
    message_id = Column(Integer, nullable=False)
    topic_id = Column(Integer, nullable=True)  # For forum groups
    topic_name = Column(String(255), nullable=True)
    sender_id = Column(BigInteger)
    sender_username = Column(String(255))
    sender_first_name = Column(String(255))
    sender_last_name = Column(String(255))
    message_type = Column(String(50), nullable=False)  # text, photo, video, document, etc.
    text_content = Column(Text)
    caption = Column(Text)
    file_id = Column(String(255))  # For media files
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db():
    """Initialize the database - creates tables automatically."""
    engine = create_engine(DATABASE_URL, echo=False)
    # This line creates ALL tables defined in models above
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session."""
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
