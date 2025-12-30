"""Interactive reinitialize command with buttons."""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler
)
from reinitialize import ReinitializationHandler
from db_handler import DatabaseHandler
import config

logger = logging.getLogger(__name__)

# Conversation states
SELECT_SOURCE, SELECT_TARGET, CONFIRM = range(3)


def is_admin(user_id):
    """Check if a user is an admin."""
    return user_id in config.ADMIN_IDS


async def start_reinitialize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start interactive reinitialize process."""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return ConversationHandler.END
    
    # Get all groups
    groups = DatabaseHandler.get_all_groups()
    
    if len(groups) < 2:
        await update.message.reply_text(
            "❌ You need at least 2 groups to reinitialize.\n"
            f"Currently monitoring: {len(groups)} group(s)"
        )
        return ConversationHandler.END
    
    # Create buttons for source selection
    keyboard = []
    for group in groups:
        button_text = f"{group['group_name']} ({group['message_count']} msgs)"
        callback_data = f"src_{group['group_id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔄 **Reinitialize: Step 1/2**\n\n"
        "Select the **source group** (where to copy messages FROM):\n\n"
        "⚠️ Note: Large migrations may timeout on Vercel (10s limit).",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SELECT_SOURCE


async def select_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle source group selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Reinitialize cancelled.")
        return ConversationHandler.END
    
    # Extract group_id from callback_data
    source_id = int(query.data.replace("src_", ""))
    context.user_data['source_id'] = source_id
    
    # Get source group info
    groups = DatabaseHandler.get_all_groups()
    source_group = next((g for g in groups if g['group_id'] == source_id), None)
    
    if not source_group:
        await query.edit_message_text("❌ Source group not found.")
        return ConversationHandler.END
    
    context.user_data['source_name'] = source_group['group_name']
    
    # Create buttons for target selection (exclude source)
    keyboard = []
    for group in groups:
        if group['group_id'] != source_id:
            button_text = f"{group['group_name']}"
            callback_data = f"tgt_{group['group_id']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data="back")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔄 **Reinitialize: Step 2/2**\n\n"
        f"✅ Source: **{source_group['group_name']}** ({source_group['message_count']} messages)\n\n"
        f"Select the **target group** (where to copy messages TO):",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SELECT_TARGET


async def select_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle target group selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Reinitialize cancelled.")
        return ConversationHandler.END
    
    if query.data == "back":
        # Go back to source selection
        return await start_reinitialize_from_callback(update, context)
    
    # Extract group_id from callback_data
    target_id = int(query.data.replace("tgt_", ""))
    context.user_data['target_id'] = target_id
    
    # Get target group info
    groups = DatabaseHandler.get_all_groups()
    target_group = next((g for g in groups if g['group_id'] == target_id), None)
    
    if not target_group:
        await query.edit_message_text("❌ Target group not found.")
        return ConversationHandler.END
    
    context.user_data['target_name'] = target_group['group_name']
    
    # Confirmation
    keyboard = [
        [InlineKeyboardButton("✅ Start Reinitialize", callback_data="confirm")],
        [InlineKeyboardButton("◀️ Back", callback_data="back")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    source_name = context.user_data['source_name']
    source_id = context.user_data['source_id']
    
    # Get message count
    groups = DatabaseHandler.get_all_groups()
    source_group = next((g for g in groups if g['group_id'] == source_id), None)
    msg_count = source_group['message_count'] if source_group else 0
    
    await query.edit_message_text(
        f"🔄 **Ready to Reinitialize**\n\n"
        f"📤 Source: **{source_name}**\n"
        f"📥 Target: **{target_group['group_name']}**\n"
        f"📊 Messages: {msg_count:,}\n\n"
        f"⚠️ This will copy all messages and topics to the target group.\n\n"
        f"Proceed?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return CONFIRM


async def confirm_and_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute the reinitialize process."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Reinitialize cancelled.")
        return ConversationHandler.END
    
    if query.data == "back":
        # Go back to target selection
        return await select_source_from_callback(update, context)
    
    if query.data != "confirm":
        return CONFIRM
    
    # Get stored IDs
    source_id = context.user_data.get('source_id')
    target_id = context.user_data.get('target_id')
    source_name = context.user_data.get('source_name')
    target_name = context.user_data.get('target_name')
    
    # Start processing
    status_message = await query.edit_message_text(
        f"🔄 **Starting reinitialization...**\n\n"
        f"Source: `{source_name}`\n"
        f"Target: `{target_name}`\n\n"
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
            pass
    
    # Perform reinitialization
    try:
        handler = ReinitializationHandler(context.bot)
        result = await handler.reinitialize(
            source_id,
            target_id,
            progress_callback
        )
        
        # Format result
        result_text = (
            f"✅ **Reinitialization Complete**\n\n"
            f"Messages sent: {result['sent']:,}\n"
            f"Messages failed: {result['failed']:,}\n"
            f"Topics created: {result['topics_created']}\n"
        )
        
        if result['errors']:
            result_text += f"\n⚠️ **Errors:** {len(result['errors'])}\n"
            for error in result['errors'][:5]:
                result_text += f"• Message {error['message_id']}: {error['error']}\n"
            if len(result['errors']) > 5:
                result_text += f"• ... and {len(result['errors']) - 5} more errors\n"
        
        await status_message.edit_text(result_text, parse_mode='Markdown')
        logger.info(f"Reinitialization completed: {source_id} -> {target_id}")
    
    except Exception as e:
        await status_message.edit_text(
            f"❌ **Reinitialization Failed**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please check that:\n"
            f"• Bot is admin in both groups\n"
            f"• Group IDs are correct"
        )
        logger.error(f"Reinitialization error: {e}", exc_info=True)
    
    return ConversationHandler.END


async def start_reinitialize_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart from callback (for back button)."""
    query = update.callback_query
    
    groups = DatabaseHandler.get_all_groups()
    
    keyboard = []
    for group in groups:
        button_text = f"{group['group_name']} ({group['message_count']} msgs)"
        callback_data = f"src_{group['group_id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 **Reinitialize: Step 1/2**\n\n"
        "Select the **source group** (where to copy messages FROM):",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SELECT_SOURCE


async def select_source_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to target selection."""
    source_id = context.user_data.get('source_id')
    source_name = context.user_data.get('source_name')
    
    groups = DatabaseHandler.get_all_groups()
    source_group = next((g for g in groups if g['group_id'] == source_id), None)
    
    query = update.callback_query
    
    keyboard = []
    for group in groups:
        if group['group_id'] != source_id:
            button_text = f"{group['group_name']}"
            callback_data = f"tgt_{group['group_id']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("◀️ Back", callback_data="back")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔄 **Reinitialize: Step 2/2**\n\n"
        f"✅ Source: **{source_name}** ({source_group['message_count']} messages)\n\n"
        f"Select the **target group** (where to copy messages TO):",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SELECT_TARGET


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END


# Create the conversation handler
def get_reinitialize_handler():
    """Get the reinitialize conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler('reinitialize', start_reinitialize)],
        states={
            SELECT_SOURCE: [
                CallbackQueryHandler(select_source)
            ],
            SELECT_TARGET: [
                CallbackQueryHandler(select_target)
            ],
            CONFIRM: [
                CallbackQueryHandler(confirm_and_execute)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
