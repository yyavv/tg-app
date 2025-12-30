# Quick Start Guide

## Setup in 5 Minutes

### 1. Get Bot Token

- Open Telegram
- Search for `@BotFather`
- Send `/newbot`
- Choose a name and username
- Copy the token

### 2. Get Your User ID

- Search for `@userinfobot` in Telegram
- Start the bot
- Copy your user ID

### 3. Configure Bot

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add:
BOT_TOKEN=your_token_from_botfather
ADMIN_IDS=your_user_id
```

### 4. Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

### 5. Add to Group

- Add your bot to a Telegram group
- Make it an **administrator**
- Send a message - it will be captured!

## First Commands

```
/status - Check if bot is working
/list_groups - See captured groups
```

## Example Migration

```bash
# 1. Check your groups
/list_groups

# You'll see:
# • Old Group
#   ID: -1001234567890
#   Messages: 100

# 2. Create new group and add bot

# 3. Get new group ID
/list_groups

# You'll see both groups now

# 4. Migrate
/reinitialize -1001234567890 -1009876543210
```

Done! All messages are now in the new group.

## Troubleshooting

**Bot doesn't respond?**

- Check BOT_TOKEN in .env
- Make sure bot.py is running

**Not capturing messages?**

- Make bot an administrator
- Give it "Read messages" permission

**Can't migrate?**

- Bot must be admin in BOTH groups
- Check group IDs are correct

## Need Help?

Check the full [README.md](README.md) for detailed documentation.
