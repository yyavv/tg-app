"""Reinitialize command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from reinitialize import ReinitializationHandler
import config

logger = logging.getLogger(__name__)


def is_admin(user_id):
    """Check if a user is an admin."""
    return user_id in config.ADMIN_IDS


async def reinitialize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reinitialize command."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    
    # Warning: This command doesn't work in webhook mode (Vercel timeout)
    await update.message.reply_text(
        "⚠️ **Warning: Reinitialize Not Available in Webhook Mode**\n\n"
        "This command requires sending hundreds of messages, which takes too long "
        "for Vercel's 10-second timeout limit.\n\n"
        "**Alternative Solutions:**\n"
        "1️⃣ Use `/export` to download messages as JSON\n"
        "2️⃣ Manually forward important messages\n"
        "3️⃣ Run bot in polling mode locally for migration\n\n"
        "If you need to migrate a large group, run `python bot_polling.py` locally "
        "and use `/reinitialize` there.",
        parse_mode='Markdown'
    )
    return
    
    # Parse arguments (disabled for webhook mode)
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Invalid usage.\n\n"
            "Usage: `/reinitialize <source_group_id> <target_group_id>`\n\n"
            "Example: `/reinitialize -1001234567890 -1009876543210`",
            parse_mode='Markdown'
        )
        return
    
    try:
        source_group_id = int(context.args[0])
        target_group_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Group IDs must be valid integers.")
        return
    
    # Send starting message
    status_message = await update.message.reply_text(
        f"🔄 **Starting reinitialization...**\n\n"
        f"Source: `{source_group_id}`\n"
        f"Target: `{target_group_id}`\n\n"
        f"Please wait...",
        parse_mode='Markdown'
    )
    
    # Progress callback
    async def progress_callback(current, total):
        progress_text = (
            f"🔄 **Reinitialization in progress...**\n\n"
            f"Progress: {current:,}/{total:,} messages\n"
            f"Percentage: {(current/total*100):.1f}%"
        )
        try:
            await status_message.edit_text(progress_text, parse_mode='Markdown')
        except Exception:
            pass  # Ignore edit errors
    
    # Perform reinitialization
    try:
        handler = ReinitializationHandler(context.bot)
        result = await handler.reinitialize(
            source_group_id,
            target_group_id,
            progress_callback
        )
        
        # Format result message
        result_text = (
            f"✅ **Reinitialization Complete**\n\n"
            f"Messages sent: {result['sent']:,}\n"
            f"Messages failed: {result['failed']:,}\n"
            f"Topics created: {result['topics_created']}\n"
        )
        
        # Add error details if any
        if result['errors']:
            result_text += f"\n⚠️ **Errors encountered:** {len(result['errors'])}\n"
            # Show first 5 errors
            for error in result['errors'][:5]:
                result_text += f"• Message {error['message_id']}: {error['error']}\n"
            if len(result['errors']) > 5:
                result_text += f"• ... and {len(result['errors']) - 5} more errors\n"
        
        await status_message.edit_text(result_text, parse_mode='Markdown')
        logger.info(f"Reinitialization completed by {user.username}: {source_group_id} -> {target_group_id}")
    
    except ValueError as e:
        await status_message.edit_text(f"❌ **Reinitialization Failed**\n\n{str(e)}")
        logger.error(f"Reinitialization failed: {e}")
    
    except Exception as e:
        await status_message.edit_text(
            f"❌ **Reinitialization Failed**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please check that:\n"
            f"• The bot is a member of both groups\n"
            f"• The bot has admin rights in both groups\n"
            f"• The group IDs are correct"
        )
        logger.error(f"Reinitialization error: {e}", exc_info=True)
