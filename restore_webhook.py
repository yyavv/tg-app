"""Restore Telegram webhook for Vercel."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in .env file!")
    exit(1)

if not WEBHOOK_URL:
    print("❌ WEBHOOK_URL not found in .env file!")
    print("Add this to .env:")
    print("WEBHOOK_URL=https://vercel-tg-app.vercel.app")
    exit(1)

# Set webhook
url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
data = {
    'url': f"{WEBHOOK_URL}/webhook"
}

if WEBHOOK_SECRET:
    data['secret_token'] = WEBHOOK_SECRET

print(f"🔄 Setting webhook to: {WEBHOOK_URL}/webhook")

response = requests.post(url, json=data)
result = response.json()

if result.get('ok'):
    print("✅ Webhook set successfully!")
    print(f"   URL: {WEBHOOK_URL}/webhook")
    print(f"   Secured: {bool(WEBHOOK_SECRET)}")
else:
    print(f"❌ Error: {result.get('description')}")

# Verify
status_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
status = requests.get(status_url).json()

if status.get('ok'):
    info = status.get('result', {})
    print(f"\n📊 Webhook Status:")
    print(f"   URL: {info.get('url', 'None')}")
    print(f"   Pending updates: {info.get('pending_update_count', 0)}")
    print(f"\n✅ Vercel bot is now active!")
