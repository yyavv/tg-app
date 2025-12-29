#!/usr/bin/env python3
"""Generate a random secret token for webhook security."""
import secrets
import string

def generate_secret(length=32):
    """Generate a cryptographically secure random secret."""
    # Use letters, digits, and some special characters
    alphabet = string.ascii_letters + string.digits + '-._~'
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret

if __name__ == '__main__':
    secret = generate_secret(32)
    print("=" * 60)
    print("🔐 WEBHOOK SECRET TOKEN")
    print("=" * 60)
    print(f"\n{secret}\n")
    print("=" * 60)
    print("\n✅ Bunu kopyala ve Vercel Environment Variables'a ekle:")
    print("   Name:  WEBHOOK_SECRET")
    print(f"   Value: {secret}")
    print("\n⚠️  Bu secret'ı kimseyle paylaşma!")
    print("=" * 60)
