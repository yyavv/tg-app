# Telegram Message Capture Bot

A powerful Telegram bot that captures messages from groups and enables migration between groups with full message history preservation.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[TOPICS_GUIDE.md](TOPICS_GUIDE.md)** - Complete guide to forum topic support ⭐
- **[EXAMPLE_MIGRATION.md](EXAMPLE_MIGRATION.md)** - Real-world migration walkthrough
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference and quick lookup
- **[INDEX.md](INDEX.md)** - Full documentation index

## Features

- 📝 **Automatic Message Capture**: Captures all message types (text, photos, videos, documents, etc.)
- 🗂️ **Advanced Forum Support**: **Complete topic tracking** - captures which group AND which topic for every message
- 🎯 **Topic-Aware Migration**: Preserves entire forum structure with all topics during migration
- 🔄 **Group Migration**: Transfer entire message history to new groups
- 📊 **Statistics**: Track groups, topics, and message counts per topic
- 🔐 **Admin Controls**: Secure admin-only commands
- ⚡ **Rate Limiting**: Smart handling of Telegram rate limits

## Why This Bot is Special for Forum Groups

**Every message knows its exact location:**

- ✅ Group ID and Name
- ✅ Topic ID and Name (for forum messages)
- ✅ Sender information
- ✅ Full message content
- ✅ Timestamp

**Perfect for:**

- Migrating forum groups with multiple topics
- Tracking team discussions by topic
- Department/project-based organization
- Preserving complex group structures

See [TOPICS_GUIDE.md](TOPICS_GUIDE.md) for detailed topic functionality.

## Supported Message Types

- Text messages
- Photos
- Videos
- Documents
- Audio files
- Voice messages
- Video notes
- Stickers
- Animations
- Locations
- Polls

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd tg-app
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# Get token from @BotFather
BOT_TOKEN=your_bot_token_here

# Get your user ID from @userinfobot
ADMIN_IDS=123456789,987654321

# Database path (default is fine)
DATABASE_PATH=bot_database.db

# Logging level
LOG_LEVEL=INFO
```

### 5. Run the Bot

```bash
python bot.py
```

## Getting Started

### Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the token and add it to `.env`

### Get Your User ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Start the bot
3. Copy your user ID and add it to `.env` as ADMIN_IDS

### Add Bot to Group

1. Add your bot to the Telegram group
2. Make the bot an **administrator** (required for capturing messages)
3. Messages will automatically be captured

## Commands

### For Everyone

- `/start` - Start the bot and see welcome message
- `/help` - Show help information

### For Admins Only

- `/status` - Show database statistics (groups, topics, messages)
- `/list_groups` - List all monitored groups with IDs and message counts
- `/list_topics <group_id>` - **Show all topics in a forum group with message counts**
- `/reinitialize <source_id> <target_id>` - Migrate messages between groups

## Usage Examples

### Example 1: Basic Message Capture

1. Add bot to "Team Chat" group
2. Make bot an admin
3. Messages are automatically captured
4. Check with `/list_groups`

### Example 2: Forum Group with Topics

**Scenario:** Track messages by topic in a forum group

1. Add bot to "Development Forum" (forum group)
2. Make bot admin
3. Messages in all topics are captured with topic information

**Check topics:**

```
You: /list_topics -1001234567890

Bot: 📋 Topics in Development Forum

📌 General
   Topic ID: 1
   Messages: 50

📌 Backend
   Topic ID: 2
   Messages: 120

📌 Frontend
   Topic ID: 3
   Messages: 80

Total Messages: 250
```

### Example 3: Migrate to New Group

```
You: /list_groups

Bot: 📋 Monitored Groups:

• Old Team Chat
  ID: -1001234567890
  Messages: 500
  Topics: 1

You: /reinitialize -1001234567890 -1009876543210

Bot: 🔄 Starting reinitialization...
     ... (progress updates) ...
     ✅ Reinitialization Complete
     Messages sent: 498
     Messages failed: 2
```

### Example 4: Forum Group Migration with Topics

**Complete topic structure preservation:**

**Source Forum:**

```
Development Forum (-1001111111111)
├── General - 50 messages
├── Backend - 120 messages
├── Frontend - 80 messages
└── DevOps - 45 messages
```

**Migration:**

```
You: /reinitialize -1001111111111 -1002222222222

Bot: 🔄 Starting reinitialization...
     Creating topics...
     ✅ Created topic 'General'
     ✅ Created topic 'Backend'
     ✅ Created topic 'Frontend'
     ✅ Created topic 'DevOps'

     ... (progress updates) ...

     ✅ Reinitialization Complete
     Messages sent: 293
     Messages failed: 2
     Topics created: 4
```

**Result - New forum has identical structure:**

```
New Development Forum (-1002222222222)
├── General - 50 messages ✅
├── Backend - 120 messages ✅
├── Frontend - 80 messages ✅
└── DevOps - 43 messages ✅
```

For detailed topic examples, see [TOPICS_GUIDE.md](TOPICS_GUIDE.md).

## Database Structure

The bot uses SQLite to store:

- **Groups**: Group IDs, names, and metadata
- **Topics**: **Forum topic IDs and names** (crucial for topic tracking)
- **Messages**: Complete message data including:
  - **Group ID and name** (which group)
  - **Topic ID and name** (which topic in the group)
  - Sender information
  - Message type and content
  - File IDs for media
  - Timestamps

### Topic Tracking Example

```python
# Every message stores its exact location:
{
    'group_id': -1001234567890,      # Which group
    'group_name': 'Dev Forum',       # Group name
    'topic_id': 12345,               # Which topic  ✨
    'topic_name': 'Backend',         # Topic name   ✨
    'message_id': 789,
    'text_content': 'Bug fixed!',
    'timestamp': '2025-12-29T10:30:00'
}
```

## Rate Limiting

The bot handles Telegram's rate limits automatically:

- Default: 20 messages per second
- Automatic retry on flood control
- Progress updates during large migrations
- Configurable in `config.py`

## Error Handling

The bot provides detailed error reporting:

- File expiry notifications
- Permission errors
- Message length issues
- Network problems

Failed messages are logged and reported after reinitialization.

## Project Structure

```
tg-app/
├── bot.py                 # Main bot file
├── config.py              # Configuration management
├── database.py            # Database models
├── db_handler.py          # Database operations
├── message_handlers.py    # Message capture logic
├── admin_commands.py      # Admin command handlers
├── reinit_command.py      # Reinitialize command
├── reinitialize.py        # Reinitialization logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration Options

Edit `config.py` to customize:

- `MESSAGES_PER_SECOND`: Rate limiting (default: 20)
- `FLOOD_WAIT_TIME`: Retry wait time (default: 30s)
- `MAX_MESSAGE_LENGTH`: Max text length (default: 4096)
- `PROGRESS_UPDATE_INTERVAL`: Update frequency (default: 100)

## Troubleshooting

### Bot doesn't capture messages

- Ensure bot is an **administrator** in the group
- Check that bot has "Read messages" permission
- Verify bot token is correct

### Reinitialization fails

- Verify bot is admin in **both** groups
- Check group IDs are correct (use `/list_groups`)
- Ensure target group exists and bot is a member

### File not found errors during reinitialization

- File IDs expire after some time
- Reinitialize soon after capturing messages
- Some old media may not be available

## Security Notes

- Keep your `.env` file secure and never commit it
- Only share admin access with trusted users
- Bot token gives full control - keep it private
- Review admin user IDs carefully

## Tips for Best Results

1. **Regular Monitoring**: Use `/status` to check captured messages
2. **Test First**: Try with a small group before large ones
3. **Keep Backup**: Don't delete original group until verified
4. **Timely Migration**: Migrate soon to avoid file expiry
5. **Admin Rights**: Always ensure bot has admin permissions
6. **Be Patient**: Large groups take time - monitor progress

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

MIT License - feel free to use and modify as needed.

## Support

For issues or questions:

- Check this README
- Review error messages carefully
- Ensure all prerequisites are met
- Contact the bot administrator

## Changelog

### Version 1.0.0

- Initial release
- Message capture functionality
- Forum group support
- Reinitialization feature
- Admin commands
- Rate limiting
- Error handling

---

Made with ❤️ for Telegram group management
