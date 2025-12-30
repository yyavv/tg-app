"""Delete Telegram webhook to run bot locally."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in .env file!")
    exit(1)

# Delete webhook
url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
print(f"🔄 Deleting webhook...")

response = requests.get(url)
result = response.json()

if result.get('ok'):
    print("✅ Webhook deleted successfully!")
    print("You can now run: python bot_polling.py")
else:
    print(f"❌ Error: {result.get('description')}")

# Show current status
status_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
status = requests.get(status_url).json()

if status.get('ok'):
    webhook_url = status.get('result', {}).get('url', '')
    if webhook_url:
        print(f"\n⚠️ Warning: Webhook still set to: {webhook_url}")
    else:
        print("\n✅ No webhook configured. Bot ready for polling mode!")
