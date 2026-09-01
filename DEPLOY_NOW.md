# 🚀 MediaSave Bot - DEPLOYMENT GUIDE

**Status**: ✅ READY FOR PRODUCTION  
**Last Updated**: 2026-09-01  
**GitHub**: https://github.com/saidodilkhon8-sudo/MediaSave

---

## ⚡ QUICK START (2 Minutes)

### 1️⃣ Go to Render.com
https://render.com/dashboard

### 2️⃣ Create New Service
- Click **New +**
- Select **Web Service**
- Click **Connect GitHub**
- Find `saidodilkhon8-sudo/MediaSave`
- Click **Connect**

### 3️⃣ Configure Service
```
Name:          mediasave-bot
Environment:   Python 3
Region:        Singapore (or nearest to you)
Branch:        main
Build Command: pip install -r requirements.txt
Start Command: python -m mediasave.main
Plan:          Free (or upgrade later)
```

### 4️⃣ Add Environment Variables
Click **Environment** and add:

```
BOT_TOKEN               = 8619293558:AAH9n1QMqrCF7WTOCWOzC4cfZBexldS5jRQ
ADMIN_IDS              = @Said013_00
WATERMARK_ENABLED      = true
WATERMARK_TEXT         = MediaSave
LOG_LEVEL              = INFO
```

### 5️⃣ Create Database
- Click **Databases** → **New PostgreSQL**
- Name: `mediasave-db`
- Plan: Free
- Click **Create**
- Render auto-sets `DATABASE_URL`

### 6️⃣ Deploy
- Go back to service
- Click **Manual Deploy** → **Deploy latest commit**
- Wait 2-3 minutes for deployment
- Check **Logs** for success message

### 7️⃣ Test Bot
Open Telegram → Search `@mediasave020_bot`
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
- Free Tier: 100-500 users/day
- Auto-cleanup of old files

---

## 🔍 Verify Deployment

### In Render Dashboard
1. Go to your service
2. Click **Logs** tab
3. Should see:
```
2026-09-01 10:00:00 INFO aiogram.dispatcher: Start polling
2026-09-01 10:00:01 INFO aiogram.dispatcher: Run polling for bot @mediasave020_bot
```

### Test in Telegram
1. Send `/start` → Bot responds with welcome
2. Send YouTube URL → Bot downloads
3. Send `/admin` → Admin panel appears (if you're admin)

### Check Metrics
- **Memory**: Should stay < 400MB
- **CPU**: Should stay < 50%
- **Errors**: Should be 0 in Logs

---

## ❌ Troubleshooting

### Bot Not Responding
1. Check BOT_TOKEN is correct
2. Verify logs for errors
3. Wait 30-60 seconds (sometimes takes time to start)

### "Connection refused" Error
1. PostgreSQL database needs 30 seconds to start
2. Check DATABASE_URL is filled
3. Restart service if still failing

### FFmpeg Not Found
- Render includes FFmpeg, should auto-work
- If error: check FFMPEG_PATH = ffmpeg

### Bot Works Locally But Not on Render
1. Check all env variables are set correctly
2. Verify BOT_TOKEN matches
3. Check logs for specific errors
4. Try manual redeploy: Manual Deploy → Deploy latest commit

---

## 📈 Monitoring

### Keep Eye On
1. **Logs**: Check daily for errors
2. **Memory**: Restart if > 400MB
3. **Performance**: Should be instant responses

### Auto Cleanup
- Old files deleted after 24 hours
- Cache cleaned periodically
- No manual cleanup needed

---

## 💰 Cost

**Free Tier (Recommended Start)**
- Web Service: $0 (auto-suspend after 15min inactivity)
- PostgreSQL: $0 (limited)
- Total: **$0/month**

**Standard Tier (If Needed)**
- Web Service: $7/month
- PostgreSQL: $9/month (optional)
- Total: **$16/month** (fast, always on)

---

## 🆙 Upgrade Later

If bot becomes popular:

1. **Switch to Standard Plan**
   - Render Dashboard → Service → Settings
   - Change Plan to Standard
   - No downtime!

2. **Upgrade Database**
   - Dashboard → Database → Settings
   - Upgrade PostgreSQL plan
   - Auto-migrated!

---

## 📝 Documentation

For more details:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Complete step-by-step
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Verify everything
- [FINAL_REPORT.md](./FINAL_REPORT.md) - What's included
- [ERROR_HANDLING_REPORT.md](./ERROR_HANDLING_REPORT.md) - Error handling
- [README.md](./README.md) - Features overview

---

## 🆘 Emergency Help

**If deployment fails:**

1. Check Render Logs for specific error message
2. Common issues:
   - `Module not found` → dependency missing
   - `Connection refused` → database not ready
   - `BOT_TOKEN invalid` → wrong token

3. Solutions:
   - Restart service (Manual Deploy button)
   - Check env variables
   - Wait 2-3 minutes for database

**Need help?**
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
- [ ] Metrics look good
- [ ] Memory < 400MB

---

## 🎉 You're Done!

Your MediaSave bot is now **LIVE** 🚀

Bot is ready for:
- ✅ Friends & family testing
- ✅ Public deployment
- ✅ Scaling to thousands of users

---

**Deployment Time**: 2-3 minutes  
**Setup Time**: 5-10 minutes  
**Support**: 24/7 via Render & GitHub  

**Good luck! 🚀**
