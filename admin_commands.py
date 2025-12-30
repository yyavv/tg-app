"""Admin command handlers for the Telegram bot."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from db_handler import DatabaseHandler
import config

logger = logging.getLogger(__name__)


def is_admin(user_id):
    """Check if a user is an admin."""
    return user_id in config.ADMIN_IDS


class AdminCommands:
    """Admin command handlers."""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        
        welcome_message = f"""
👋 Hello {user.first_name}!

I'm a message capture bot. Add me to your groups to start capturing messages.

**Features:**
• Automatic message capture from groups
• Support for forum topics
• Group migration with /reinitialize

**Admin Commands:**
/status - Database statistics
/stats - Detailed statistics with charts
/recent [N] - Show last N messages (default 10)
/list_groups - List all monitored groups
/list_topics <group_id> - Show topics in a group
/reinitialize - Migration info (not available in webhook mode)

**Setup:**
1. Add me to your group
2. Make me an admin
3. Messages will be captured automatically

For help, contact the bot administrator.
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    @staticmethod
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("⛔ You are not authorized to use this command.")
            return
        
        stats = DatabaseHandler.get_database_stats()
        
        status_message = f"""
📊 **Database Status**

Groups monitored: {stats['groups']}
Total topics: {stats['topics']}
Total messages: {stats['messages']:,}
"""
        await update.message.reply_text(status_message, parse_mode='Markdown')
        logger.info(f"Status command used by {user.username}")
    
    @staticmethod
    async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_groups command."""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("⛔ You are not authorized to use this command.")
            return
        
        groups = DatabaseHandler.get_all_groups()
        
        if not groups:
            await update.message.reply_text("📋 No groups are being monitored yet.")
            return
        
        message = "📋 **Monitored Groups:**\n\n"
        for group in groups:
            message += f"• {group['group_name']}\n"
            message += f"  ID: `{group['group_id']}`\n"
            message += f"  Messages: {group['message_count']:,}\n"
            message += f"  Topics: {group['topic_count']}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"List groups command used by {user.username}")
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
🤖 **Bot Help**

**For Everyone:**
/start - Start the bot and see welcome message
/help - Show this help message

**For Admins:**
/status - Show database statistics
/list_topics <group_id> - Show topics in a specific group
/list_groups - List all monitored groups
/reinitialize <source_id> <target_id> - Migrate messages from one group to another

**How to Use:**
1. Add the bot to your Telegram group
2. Make the bot an administrator
3. Messages will be automatically captured
4. Use /list_groups to see captured groups and their IDs
5. Use /reinitialize to migrate messages to a new group

**Example:**
`/reinitialize -1001234567890 -1009876543210`

This will copy all messages from the source group to the target group.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @staticmethod
    async def list_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_topics command to show topics in a group."""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("⛔ You are not authorized to use this command.")
            return
        
        # Parse group_id argument
        if len(context.args) != 1:
            await update.message.reply_text(
                "❌ Invalid usage.\n\n"
                "Usage: `/list_topics <group_id>`\n\n"
                "Example: `/list_topics -1001234567890`\n\n"
                "Use /list_groups to get group IDs.",
                parse_mode='Markdown'
            )
            return
        
        try:
            group_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Group ID must be a valid integer.")
            return
        
        # Get group info
        group = DatabaseHandler.get_group_by_id(group_id)
        if not group:
            await update.message.reply_text(f"❌ Group with ID `{group_id}` not found in database.", parse_mode='Markdown')
            return
        
        # Get topic statistics
        topic_stats = DatabaseHandler.get_topic_stats(group_id)
        
        if not topic_stats:
            await update.message.reply_text(
                f"📋 **Topics in {group.group_name}**\n\n"
                f"No messages captured yet for this group.",
                parse_mode='Markdown'
            )
            return
        
        message = f"📋 **Topics in {group.group_name}**\n"
        message += f"Group ID: `{group_id}`\n\n"
        
        total_messages = 0
        for topic in topic_stats:
            topic_name = topic['topic_name']
            topic_id = topic['topic_id']
            msg_count = topic['message_count']
            total_messages += msg_count
            
            if topic_id is None:
                message += f"📌 **{topic_name}** (No topic)\n"
            else:
                message += f"📌 **{topic_name}**\n"
                message += f"   Topic ID: `{topic_id}`\n"
            message += f"   Messages: {msg_count:,}\n\n"
        
        message += f"**Total Messages:** {total_messages:,}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"List topics command used by {user.username} for group {group_id}")
    
    @staticmethod
    async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recent command - Show recent messages."""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("⛔ You are not authorized to use this command.")
            return
        
        # Parse limit argument (default 10)
        limit = 10
        if context.args and context.args[0].isdigit():
            limit = min(int(context.args[0]), 50)  # Max 50 messages
        
        messages = DatabaseHandler.get_recent_messages(limit=limit)
        
        if not messages:
            await update.message.reply_text("📭 No messages in database yet.")
            return
        
        # Group consecutive messages from same group/topic
        grouped = []
        current_group = None
        
        for msg in messages:
            group_key = (msg.group_id, msg.topic_id)
            
            if current_group and current_group['key'] == group_key:
                # Add to current group
                current_group['messages'].append(msg)
                current_group['count'] += 1
            else:
                # Start new group
                if current_group:
                    grouped.append(current_group)
                
                current_group = {
                    'key': group_key,
                    'group_name': msg.group_name,
                    'topic_name': msg.topic_name,
                    'messages': [msg],
                    'count': 1
                }
        
        if current_group:
            grouped.append(current_group)
        
        response = f"📬 **Recent Messages ({len(messages)} total)**\n\n"
        
        for group in grouped:
            # Topic info
            topic_info = f" • {group['topic_name']}" if group['topic_name'] else ""
            
            # Show group header
            if group['count'] == 1:
                msg = group['messages'][0]
                timestamp = msg.timestamp.strftime("%H:%M")
                sender = msg.sender_username or msg.sender_first_name or "Unknown"
                
                # Message preview
                if msg.text_content:
                    preview = msg.text_content[:60]
                    if len(msg.text_content) > 60:
                        preview += "..."
                elif msg.caption:
                    preview = f"[{msg.message_type}] {msg.caption[:40]}..."
                else:
                    preview = f"[{msg.message_type}]"
                
                response += f"🔹 **{group['group_name']}**{topic_info}\n"
                response += f"   👤 {sender} • {timestamp}\n"
                response += f"   💬 {preview}\n\n"
            else:
                # Multiple messages - show count
                first_msg = group['messages'][0]
                last_msg = group['messages'][-1]
                time_range = f"{last_msg.timestamp.strftime('%H:%M')}-{first_msg.timestamp.strftime('%H:%M')}"
                
                response += f"🔹 **{group['group_name']}**{topic_info}\n"
                response += f"   📦 {group['count']} messages • {time_range}\n"
                
                # Show preview of last message
                msg = group['messages'][0]  # Most recent (first in list)
                if msg.text_content and len(msg.text_content) <= 40:
                    response += f"   💬 Latest: {msg.text_content}\n"
                elif msg.message_type != "text":
                    response += f"   💬 Latest: [{msg.message_type}]\n"
                
                response += "\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Recent command used by {user.username}, limit={limit}")
    
    @staticmethod
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - Show detailed statistics."""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("⛔ You are not authorized to use this command.")
            return
        
        stats = DatabaseHandler.get_detailed_stats()
        
        message = "📊 **Detailed Statistics**\n\n"
        
        # Overall stats
        message += f"📝 **Total Messages:** {stats['total_messages']:,}\n"
        message += f"👥 **Groups Monitored:** {stats['total_groups']}\n"
        message += f"📌 **Forum Topics:** {stats['total_topics']}\n\n"
        
        # Message types
        if stats['type_stats']:
            message += "📂 **Message Types:**\n"
            for msg_type, count in stats['type_stats']:
                percentage = (count / stats['total_messages'] * 100) if stats['total_messages'] > 0 else 0
                message += f"   • {msg_type}: {count:,} ({percentage:.1f}%)\n"
            message += "\n"
        
        # Most active groups
        if stats['active_groups']:
            message += "🔥 **Most Active Groups:**\n"
            for idx, (group_id, group_name, count) in enumerate(stats['active_groups'], 1):
                message += f"   {idx}. {group_name}: {count:,} messages\n"
            message += "\n"
        
        # Most active topics
        if stats['active_topics']:
            message += "💬 **Most Active Topics:**\n"
            for idx, (topic_name, group_name, count) in enumerate(stats['active_topics'], 1):
                message += f"   {idx}. {topic_name} ({group_name}): {count:,}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"Stats command used by {user.username}")
