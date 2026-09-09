# 🚀 MediaSave Bot - DEPLOYMENT GUIDE

**Status**: ✅ READY FOR PRODUCTION  
**Last Updated**: 2026-09-09  
**GitHub**: https://github.com/saidodilkhon8-sudo/MediaSave

---

## ⚡ QUICK START

### Option 1: Deploy to Vercel (Recommended)

#### 1️⃣ Go to Vercel
https://vercel.com/dashboard

#### 2️⃣ Create New Project
- Click **New +**
- Select **Import Git Repository**
- Find `saidodilkhon8-sudo/MediaSave`
- Click **Import**

#### 3️⃣ Configure Project
```
Name:           mediasave-bot
Framework Preset: Other (or Python)
Root Directory: (leave empty - deploy from repo root)
Build Command:   pip install -r requirements.txt
Output Directory: (leave empty)
```

#### 4️⃣ Add Environment Variables
Click **Settings** → **Environment Variables** and add:

```
BOT_TOKEN             = <your_telegram_bot_token>
ADMIN_IDS             = <your_admin_telegram_id>
WATERMARK_ENABLED     = true
WATERMARK_TEXT        = MediaSave
LOG_LEVEL             = INFO
DATABASE_URL          = sqlite+aiosqlite:///mediasave.db
```

#### 5️⃣ Deploy
- Click **Deploy**
- Wait 2-3 minutes for deployment
- Check **Logs** for success message

#### 6️⃣ Test Bot
Open Telegram → Search for your bot
- Send `/start`
- Bot should respond with welcome message ✅

---

### Option 2: Deploy to Render.com

#### 1️⃣ Go to Render.com
https://render.com/dashboard

#### 2️⃣ Create New Web Service
- Click **New +**
- Select **Web Service**
- Click **Connect GitHub**
- Find `saidodilkhon8-sudo/MediaSave`
- Click **Connect**

#### 3️⃣ Configure Service
```
Name:          mediasave-bot
Environment:   Python 3
Region:        Singapore (or nearest to you)
Branch:        main
Build Command: pip install -r requirements.txt
Start Command: python -m mediasave.main
Plan:          Free (or upgrade later)
```

#### 4️⃣ Add Environment Variables
Click **Environment** and add:

```
BOT_TOKEN               = <your_telegram_bot_token>
ADMIN_IDS               = <your_admin_telegram_id>
WATERMARK_ENABLED       = true
WATERMARK_TEXT          = MediaSave
LOG_LEVEL               = INFO
```

#### 5️⃣ Create Database
- Click **Databases** → **New PostgreSQL**
- Name: `mediasave-db`
- Plan: Free
- Click **Create**
- Render auto-sets `DATABASE_URL`

#### 6️⃣ Deploy
- Go back to service
- Click **Manual Deploy** → **Deploy latest commit**
- Wait 2-3 minutes for deployment

#### 7️⃣ Test Bot
Open Telegram → Search for your bot
- Send `/start`
- Bot should respond with welcome message ✅

---

## 📊 What's Deployed

### Features
✅ Download videos from YouTube, Instagram, TikTok, etc.  
✅ Watermark "MediaSave" on all videos  
✅ Download-more button for quick re-downloads  
✅ Admin panel with `/admin` command  
✅ Real-time progress tracking (% + speed)  
✅ Music search & lyrics  
✅ Video editing (cut, MP3, thumbnail, circle)  
✅ 3 languages: Russian, English, Uzbek  

### Performance
- ~200MB memory usage
- 3 concurrent downloads
- Auto-cleanup of old files

---

## 🔍 Verify Deployment

### In Vercel Dashboard
1. Go to your project
2. Click **Logs** tab
3. Should see bot startup logs

### Test in Telegram
1. Send `/start` → Bot responds with welcome
2. Send YouTube URL → Bot downloads
3. Send `/admin` → Admin panel appears (if you're admin)

---

## ❌ Troubleshooting

### Bot Not Responding
1. Check BOT_TOKEN is correct
2. Verify logs for errors
3. Wait 30-60 seconds (sometimes takes time to start)

### FFmpeg Not Found
- Vercel/Render includes FFmpeg
- If error: check FFMPEG_PATH = ffmpeg

### Bot Works Locally But Not on Vercel
1. Check all env variables are set correctly
2. Verify BOT_TOKEN matches
3. Check logs for specific errors
4. Try redeploy: click **Deploy** again

---

## 📈 Monitoring

### Keep Eye On
1. **Logs**: Check daily for errors
2. **Memory**: Restart if > 400MB
3. **Performance**: Should be instant responses

### Auto Cleanup
- Old files deleted after 24 hours
- Cache cleaned periodically

---

## 💰 Cost

**Vercel Hobby (Recommended Start)**
- Web Service: $0
- Total: **$0/month**

**Render Free Tier**
- Web Service: $0
- PostgreSQL: $0
- Total: **$0/month**

**Standard Tier (If Needed)**
- Web Service: $7/month
- Total: **$7-16/month**

---

## 🆘 Emergency Help

**If deployment fails:**
1. Check Logs for specific error message
2. Common issues:
   - `Module not found` → dependency missing
   - `BOT_TOKEN invalid` → wrong token

3. Solutions:
   - Redeploy
   - Check env variables
   - Wait 2-3 minutes for startup

**Need help?**
- Vercel Support: https://vercel.com/support
- Render Support: https://render.com/support
- Telegram Bot issues: Check @BotFather
- GitHub Issues: Report bugs

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Bot responds to `/start`
- [ ] Can download YouTube video
- [ ] Watermark visible on video
- [ ] `/admin` command works
- [ ] No errors in Logs

---

## 🎉 You're Done!

Your MediaSave bot is now **LIVE** 🚀

**Deployment Time**: 2-3 minutes  
**Setup Time**: 5-10 minutes  

**Good luck! 🚀**
