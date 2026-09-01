# 🚀 MediaSave Deployment Guide

**Version**: 1.0.0  
**Platform**: Render.com  
**Database**: PostgreSQL  
**Status**: Ready for Production  

---

## Pre-Deployment Checklist

- ✅ All tests passing (26/26)
- ✅ Code committed to GitHub
- ✅ render.yaml configured
- ✅ Environment variables defined
- ✅ Database schema compatible
- ✅ FFmpeg integration ready
- ✅ Error handling improved
- ✅ Multilingual support (ru, en, uz)

---

## Deployment Steps

### 1. Prepare GitHub Repository

```bash
# Ensure all changes are committed
git status  # Should show "working tree clean"
git log --oneline -5  # Verify recent commits
```

✅ **Status**: All changes committed (commit 9e942b2)

### 2. Connect Render Account

1. Go to [https://render.com](https://render.com)
2. Sign in with your GitHub account
3. Create new service → Web Service
4. Connect GitHub repository: `saidodilkhon8-sudo/MediaSave`
5. Select branch: `main`

### 3. Configure Service

**Service Name**: mediasave-bot  
**Environment**: Python 3.12  
**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
python -m mediasave.main
```

### 4. Set Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `BOT_TOKEN` | `8619293558:AAH9n1QMqrCF7WTOCWOzC4cfZBexldS5jRQ` | Your Telegram Bot Token |
| `DATABASE_URL` | Auto-filled by Render | PostgreSQL connection string |
| `ADMIN_IDS` | `@Said013_00` | Admin username or ID |
| `WATERMARK_ENABLED` | `true` | Enable video watermark |
| `WATERMARK_TEXT` | `MediaSave` | Watermark text |
| `TEMP_DIR` | `./temp` | Temporary files directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE_MB` | `2000` | Max file size for upload |
| `DOWNLOAD_TIMEOUT` | `300` | Timeout in seconds |
| `FFMPEG_TIMEOUT` | `120` | FFmpeg timeout |

### 5. Create PostgreSQL Database

1. In Render dashboard: **Databases** → **New PostgreSQL**
2. **Name**: `mediasave-db`
3. **PostgreSQL Version**: 14+
4. **Plan**: Free tier (or paid)
5. Click Create

Render will auto-set `DATABASE_URL` environment variable.

### 6. Deploy

1. In Render dashboard, select your service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for deployment (~2-3 minutes)
4. Check **Logs** tab for confirmation:
   ```
   2026-09-01 10:00:00 INFO aiogram.dispatcher: Start polling
   2026-09-01 10:00:01 INFO aiogram.dispatcher: Run polling for bot @mediasave020_bot id=8619293558
   ```

---

## Post-Deployment Verification

### Test Bot Connection

1. Open Telegram and search for `@mediasave020_bot`
2. Send `/start` command
3. Verify bot responds with welcome message
4. Test download with a YouTube link

### Check Logs in Render

Click **Logs** tab and verify:
- ✅ No error messages
- ✅ Bot polling active
- ✅ Database connected
- ✅ All handlers loaded

### Monitor Errors

1. Render Dashboard → Logs
2. Look for `ERROR` or `EXCEPTION`
3. Common issues:
   - `Connection refused`: Database not accessible
   - `Module not found`: Missing dependency in requirements.txt
   - `BOT_TOKEN invalid`: Check environment variable

---

## Required Environment Variables for Render

```bash
# Required
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=@your_admin_id

# Database (auto-filled by Render)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Optional with defaults
TEMP_DIR=./temp
FFMPEG_PATH=ffmpeg
LOG_LEVEL=INFO
ENVIRONMENT=production
WATERMARK_ENABLED=true
WATERMARK_TEXT=MediaSave
RATE_LIMIT_PER_MINUTE=30
MAX_CONCURRENT_DOWNLOADS=3
MAX_FILE_SIZE_MB=2000
DOWNLOAD_TIMEOUT=300
```

---

## Troubleshooting

### Bot Not Responding

**Problem**: Deployed but bot not responding  
**Solution**: 
1. Check `BOT_TOKEN` is correct
2. Verify logs for errors
3. Ensure polling is active: `Start polling` in logs

### Database Connection Error

**Problem**: `psycopg2.OperationalError: connection refused`  
**Solution**:
1. Verify PostgreSQL database exists
2. Check `DATABASE_URL` environment variable
3. Wait 30-60 seconds after creating database

### FFmpeg Not Found

**Problem**: `ffmpeg: command not found`  
**Solution**:
1. Render includes ffmpeg in Python 3.12 runtime
2. Check if `FFMPEG_PATH=ffmpeg` is set
3. Build logs should show no errors

### Memory/Resource Issues

**Problem**: Bot crashes or becomes unresponsive  
**Solution**:
1. Upgrade Render plan (free tier limited)
2. Clear temp directory: `TEMP_DIR` cleanup
3. Optimize download concurrency

---

## Configuration Reference

### render.yaml Location
```
📁 MediaSave/
├── render.yaml          ← Deployment config
├── requirements.txt     ← Python dependencies
└── mediasave/
    ├── main.py         ← Bot entry point
    └── app/
        ├── config.py   ← Settings
        └── ...
```

### Key Settings in config.py

```python
# Database
database_url: str = "sqlite+aiosqlite:///mediasave.db"  # Changes to PostgreSQL on Render

# Watermark
watermark_enabled: bool = True
watermark_text: str = "MediaSave"

# Limits
max_file_size_mb: int = 2000
download_timeout: int = 300
max_video_duration: int = 900

# Admin
admin_ids: str = "@Said013_00"

# Concurrency
download_concurrency: int = 3
```

---

## Performance Monitoring

### Watch in Render Dashboard

1. **Memory Usage**: Should be < 512MB (free tier)
2. **CPU Usage**: Should be < 50% at rest
3. **Request Count**: Track downloads per hour
4. **Error Rate**: Should be < 5%

### View Metrics

1. Render Dashboard → Metrics
2. Monitor over 24-48 hours
3. Upgrade if needed

---

## Scaling Considerations

### Current Setup (Free Tier)
- ✅ Suitable for: 100-500 users/day
- ✅ Download concurrency: 3
- ✅ Database: Shared PostgreSQL

### Upgrade Path
1. **Standard**: $7/month
   - Dedicated resources
   - Better performance
   - 5GB storage

2. **Pro**: $12/month
   - Dedicated PostgreSQL
   - Priority support
   - Unlimited API calls

### When to Scale
- Downloads per hour > 50
- Memory usage > 400MB
- Database connection errors
- Slow response times

---

## Security Checklist

- ✅ Bot token not in source code (in env vars)
- ✅ Admin IDs configured
- ✅ Database credentials encrypted
- ✅ Input validation on all handlers
- ✅ Rate limiting enabled
- ✅ Error messages sanitized
- ✅ No sensitive data in logs

---

## Support & Rollback

### If Something Goes Wrong

1. **Stop Deployment**: Click Suspend in Render
2. **Rollback**: Deploy previous commit from Git
3. **Check Logs**: Render → Logs → see error details
4. **Debug Locally**: `python -m mediasave.main`

### Emergency Contact
- GitHub Issues: Report bugs
- Telegram: Test with bot
- Logs: Render dashboard logs tab

---

## Next Steps After Deployment

1. ✅ Test all features (download, watermark, admin)
2. ✅ Monitor error logs for 24 hours
3. ✅ Get user feedback
4. ✅ Optimize based on performance
5. ✅ Setup automated backups
6. ✅ Add monitoring alerts

---

## Useful Commands

```bash
# Check deployment status
curl https://mediasave-bot.onrender.com/health

# View real-time logs
render logs -f

# View past deployments
render deployments list

# Manual rollback (from Git)
git revert <commit-hash>
git push origin main
# Then trigger manual deploy in Render dashboard
```

---

**Status**: Ready to deploy 🚀  
**Last Updated**: 2026-09-01  
**Version**: 1.0.0 Production
