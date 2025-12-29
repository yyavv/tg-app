# Quick Reference - Topic Support

## Core Topic Features

### ✅ What Gets Captured

Every message stores:

- **Group ID** - e.g., `-1001234567890`
- **Group Name** - e.g., `"Development Forum"`
- **Topic ID** - e.g., `12345` (NULL for non-forum groups)
- **Topic Name** - e.g., `"Backend Team"` (NULL for non-forum groups)
- All message content and metadata

### ✅ Commands

```bash
# View all groups with topic counts
/list_groups

# View topics in a specific group
/list_topics -1001234567890

# Get database statistics
/status

# Migrate with topic preservation
/reinitialize -1001111111111 -1002222222222
```

## Quick Examples

### Example 1: Check Topics

```
/list_topics -1001234567890

📋 Topics in Development Forum

📌 General
   Topic ID: 1
   Messages: 150

📌 Backend
   Topic ID: 2
   Messages: 340

📌 Frontend
   Topic ID: 3
   Messages: 210
```

### Example 2: Migration Output

```
/reinitialize -1001111111111 -1002222222222

✅ Reinitialization Complete

Messages sent: 693
Messages failed: 7
Topics created: 4  ← Topics preserved!
```

## Database Quick Look

```python
# Message with topic info
{
    'group_id': -1001234567890,
    'group_name': 'Dev Forum',
    'topic_id': 2,              # ← Topic!
    'topic_name': 'Backend',    # ← Name!
    'text_content': 'Bug fixed!'
}

# Message without topic (regular group)
{
    'group_id': -1009876543210,
    'group_name': 'Team Chat',
    'topic_id': None,           # ← No topic
    'topic_name': None,         # ← Regular group
    'text_content': 'Hello!'
}
```

## Files Reference

| File                  | Purpose                           |
| --------------------- | --------------------------------- |
| `bot.py`              | Main bot, registers handlers      |
| `message_handlers.py` | Captures messages with topics     |
| `db_handler.py`       | Database operations, topic stats  |
| `admin_commands.py`   | /list_topics command              |
| `reinitialize.py`     | Migration with topic preservation |
| `database.py`         | SQLAlchemy models                 |

## Key Functions

```python
# Get topic name
DatabaseHandler.get_topic_name(group_id, topic_id)

# Get topic statistics
DatabaseHandler.get_topic_stats(group_id)
# Returns: [{topic_id, topic_name, message_count}, ...]

# Add/update topic
DatabaseHandler.add_forum_topic(group_id, topic_id, topic_name)
```

## Setup Checklist

For forum groups:

- [ ] Group is in forum mode
- [ ] Bot is added to group
- [ ] Bot has admin rights
- [ ] Topics exist or will be created
- [ ] Messages will auto-capture with topics

For migration:

- [ ] Source group captured
- [ ] Target group created (forum mode if needed)
- [ ] Bot is admin in both
- [ ] Run /reinitialize command
- [ ] Verify topics created

## Common Patterns

### Check before migration

```bash
# 1. See what you have
/list_groups

# 2. Check topics in source
/list_topics -1001111111111

# 3. Migrate
/reinitialize -1001111111111 -1002222222222

# 4. Verify target
/list_topics -1002222222222
```

### Monitor topic activity

```bash
# Regular checks
/list_topics <group_id>

# Compare message counts over time
# See which topics are most active
```

## Troubleshooting

| Issue                          | Solution                         |
| ------------------------------ | -------------------------------- |
| Topics show as "Topic 123"     | Edit topic name, bot will update |
| Topics not captured            | Make sure bot is admin           |
| Migration didn't create topics | Target must be forum group       |
| No topics showing              | Group might not be a forum       |

## Key Points

1. **Every message has location**: Group + Topic
2. **Topics auto-detected**: No manual setup needed
3. **Names captured**: Real topic names stored
4. **Migration preserves**: Topics recreated in target
5. **Statistics available**: Use /list_topics
6. **Works for regular groups too**: topic_id will be NULL

## Remember

🎯 **Group + Topic = Complete Message Location**

- Regular group: Only group info, topic is NULL
- Forum group: Both group and topic info captured
- Migration: Preserves entire structure
- Commands: See breakdown by topic

---

📚 Full docs: `README.md`, `TOPICS_GUIDE.md`, `ARCHITECTURE.md`
