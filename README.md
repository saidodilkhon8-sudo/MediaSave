# SaveX Bot

Production-ready Telegram bot for downloading and processing media from social networks.

## Features

### Platforms
- Instagram (Reels, Posts, Carousels)
- YouTube / YouTube Shorts
- X / Twitter
- Facebook
- Reddit
- Pinterest
- Threads

### Media Processing
- Download videos and images
- Create Telegram Video Notes (circles)
- Extract MP3 audio from videos
- Generate thumbnails
- Trim videos with custom start/end
- Batch download for carousels and playlists
- Retry system for failed downloads
- Music search with paginated results (YouTube)

### Infrastructure
- Queue system for concurrent downloads
- Multi-language support (RU, UZ, EN)
- Download history
- Admin panel with statistics
- Proxy support
- Cookies support
- SQLite / PostgreSQL database
- Redis support (optional)
- Docker support
- Temporary file cleanup
- Rate limiting
- File size limits
- FastAPI health checks
- Render deployment ready

## Requirements

- Python 3.12+
- FFmpeg
- Telegram Bot Token (from @BotFather)

## Installation

```bash
git clone <repo>
cd mediasave
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set BOT_TOKEN
python -m mediasave.main
```

## Music Search

The bot can search for music by artist or track name using YouTube.

### Features
- Search by artist or track name
- Paginated results (10 per page)
- Inline keyboard for selection

### Usage
1. Tap `🔍 Найти музыку` in the menu
2. Choose search mode:
   - `🎤 По исполнителю`
   - `🎵 По треку`
3. Enter your query
4. Browse results with `<-----назад` / `далее----->`
5. Select a track to download and send as audio

## Docker

```bash
docker-compose up --build
```

## Render

1. Push this repository to GitHub.
2. In Render, choose **New +** -> **Blueprint** and select the repository.
3. Set `BOT_TOKEN` in the Render environment settings.
4. Deploy the `mediasave-bot` web service and `mediasave-worker` worker.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | required |
| `DATABASE_URL` | Database URL | `sqlite+aiosqlite:///mediasave.db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `TEMP_DIR` | Temporary files directory | `./temp` |
| `MAX_FILE_SIZE_MB` | Max file size | `2000` |
| `MAX_QUEUE_SIZE` | Max queue size | `10` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per user per minute | `30` |
| `MAX_CONCURRENT_DOWNLOADS` | Max concurrent downloads | `3` |
| `DOWNLOAD_TIMEOUT` | Download timeout (s) | `300` |
| `FFMPEG_TIMEOUT` | FFmpeg timeout (s) | `120` |
| `FFMPEG_PATH` | FFmpeg executable path | `ffmpeg` |
| `YOUTUBE_COOKIES_FILE` | Optional yt-dlp cookies file | empty |
| `YOUTUBE_COOKIES_BASE64` | Optional Base64 Netscape cookies for Render | empty |
| `INSTAGRAM_COOKIES_FILE` | Optional Instagram cookies file | empty |
| `INSTAGRAM_COOKIES_BASE64` | Optional Instagram Base64 cookies | empty |
| `TWITTER_COOKIES_FILE` | Optional Twitter/X cookies file | empty |
| `TWITTER_COOKIES_BASE64` | Optional Twitter Base64 cookies | empty |
| `FACEBOOK_COOKIES_FILE` | Optional Facebook cookies file | empty |
| `FACEBOOK_COOKIES_BASE64` | Optional Facebook Base64 cookies | empty |
| `PROXY_URL` | Proxy URL (http/socks5) | empty |
| `PROXY_USERNAME` | Proxy username | empty |
| `PROXY_PASSWORD` | Proxy password | empty |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `AUTO_DELETE_HOURS` | Auto-delete temp files after hours | `24` |
| `DEFAULT_LANGUAGE` | Default language | `ru` |
| `ADMIN_IDS` | Comma-separated Telegram admin IDs | empty |

## Testing

```bash
pip install pytest pytest-asyncio
pytest
```

## Project Structure

```
mediasave/
├── app/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── messages/
│   ├── downloaders/
│   ├── media/
│   │   ├── audio_extractor.py
│   ├── database/
│   ├── services/
│   ├── i18n/
│   ├── music/
│   │   └── lyrics.py
│   └── config.py
├── tests/
├── temp/
├── logs/
├── main.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Adding a New Platform

1. Create a new downloader in `app/downloaders/` inheriting from `BaseDownloader`
2. Register it in `app/services/platform_detector.py`
3. Add translations to `app/i18n/*.json`

## License

MIT
