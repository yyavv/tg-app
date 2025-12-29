# Vercel Deployment Guide

## Adım 1: Vercel Hesabı Oluştur

1. [vercel.com](https://vercel.com) adresine git
2. GitHub hesabınla giriş yap
3. Ücretsiz hobby plan'ı seç

## Adım 2: GitHub Repository'yi Bağla

1. Bu projeyi GitHub'a push'la:

   ```bash
   git init
   git add .
   git commit -m "Initial commit - Telegram bot with webhook"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. Vercel dashboard'da "Add New Project" butonuna tıkla
3. GitHub repository'ni seç
4. Import'a tıkla

## Adım 3: Environment Variables Ayarla

Vercel dashboard'da Environment Variables bölümünde şu değişkenleri ekle:

| Key           | Value                         | Açıklama                                    |
| ------------- | ----------------------------- | ------------------------------------------- |
| `BOT_TOKEN`   | `your_bot_token`              | BotFather'dan aldığın token                 |
| `ADMIN_IDS`   | `8172818622`                  | Admin kullanıcı ID'leri (virgülle ayrılmış) |
| `WEBHOOK_URL` | `https://your-app.vercel.app` | Deploy edildikten sonra ekle                |
| `LOG_LEVEL`   | `INFO`                        | Log seviyesi (opsiyonel)                    |

⚠️ **Önemli**: İlk deploy'dan sonra Vercel URL'ini alacaksın. Sonra `WEBHOOK_URL` değişkenini güncellemelisin.

## Adım 4: Deploy Et

1. Vercel otomatik olarak deploy edecek
2. Deploy tamamlandığında URL'i kopyala (örn: `https://tg-app-xxx.vercel.app`)
3. Settings → Environment Variables → `WEBHOOK_URL` değerini bu URL ile güncelle
4. Deployments → Redeploy'a tıkla

## Adım 5: Webhook'u Ayarla

Deploy tamamlandıktan sonra tarayıcında şu URL'i ziyaret et:

```
https://your-app.vercel.app/set-webhook
```

"Webhook set to..." mesajını görmelisin.

## Test Et

1. Bot'unuzu Telegram'da bir gruba ekle
2. Grubun forum özelliğini aç (Group Settings → Topics)
3. Birkaç topic oluştur
4. Mesaj gönder
5. Admin olarak bot'a `/status` komutu gönder
6. Mesajların kaydedildiğini göreceksin

## Önemli Notlar

### Webhook vs Polling

✅ **Webhook Avantajları:**

- Ücretsiz Vercel hosting
- Telegram tüm mesajları anında sunucuna gönderir
- Hiçbir mesaj kaçmaz
- Daha az kaynak kullanımı

❌ **Webhook Dezavantajları:**

- Domain/URL gerekli (Vercel sağlıyor)
- HTTPS zorunlu (Vercel sağlıyor)

### Vercel Limitleri (Hobby Plan)

- ✅ Sınırsız deployment
- ✅ Sınırsız request (fair use)
- ✅ 100 GB bandwidth/ay
- ✅ Serverless fonksiyonlar
- ⚠️ Her request 10 saniye timeout (webhook için yeterli)

### Database

⚠️ **Önemli**: Vercel serverless ortamında SQLite dosyası her deployment'ta sıfırlanır!

**Çözümler:**

1. **PostgreSQL kullan** (Önerilen):

   - [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (ücretsiz tier: 256 MB)
   - [Neon](https://neon.tech) (ücretsiz: 512 MB)
   - [Supabase](https://supabase.com) (ücretsiz: 500 MB)

2. **MongoDB kullan**:

   - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (ücretsiz: 512 MB)

3. **SQLite'ı geçici olarak kullan**:
   - Her deployment'ta database sıfırlanır
   - Sadece test için uygun
   - Production için KULLANMA

## PostgreSQL'e Geçiş (Önerilen)

`database.py` dosyasını güncelle:

```python
import os
from sqlalchemy import create_engine

# SQLite yerine PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Vercel Postgres URL'i postgresql:// yerine postgres:// kullanıyor, düzelt
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=False)
```

`requirements.txt`'e ekle:

```
psycopg2-binary==2.9.9
```

Vercel environment variables'a ekle:

```
DATABASE_URL = <your-postgres-connection-string>
```

## Troubleshooting

### Webhook çalışmıyor?

1. Vercel logs'u kontrol et: `vercel logs`
2. Telegram webhook durumunu kontrol et: `https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo`
3. WEBHOOK_URL doğru mu kontrol et

### Database kayıtları gitmiş?

- Vercel'de SQLite kullanıyorsan normal, PostgreSQL'e geç

### Bot mesajları yakalamıyor?

1. Bot grup admini mi kontrol et
2. Bot'un mesaj okuma izni var mı kontrol et
3. Vercel logs'da hata var mı bak

## Local Test (Geliştirme)

Webhook'u local test etmek için:

1. [ngrok](https://ngrok.com) indir
2. ngrok başlat: `ngrok http 5000`
3. ngrok URL'ini `WEBHOOK_URL`'e ekle
4. Local Flask sunucu çalıştır: `python bot.py`

Veya polling mode kullan:

```bash
python bot_polling.py
```

## Yedekleme Stratejisi

Bot'unuzu yedeklemek için bot_polling.py:

```bash
# Eski polling modunu kullan
python bot_polling.py
```

Bu şekilde her iki modu da kullanabilirsin:

- **Vercel**: Webhook mode (bot.py) - Production
- **Local**: Polling mode (bot_polling.py) - Backup/Test

## Sonraki Adımlar

1. ✅ Vercel'e deploy et
2. ✅ Webhook'u ayarla
3. ✅ PostgreSQL'e geç (önemli!)
4. ✅ Bot'u test et
5. ✅ Groups ve topics ile dene
6. ✅ `/reinitialize` komutu ile migration test et

## Destek

Sorun olursa Vercel logs'u kontrol et:

```bash
vercel logs --follow
```

Veya Telegram webhook durumunu kontrol et:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```
