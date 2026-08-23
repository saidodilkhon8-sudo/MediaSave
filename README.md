# MediaSave

Production-ready Telegram bot for downloading and processing media from social networks.

## Features

- Download videos and images from YouTube, TikTok, Instagram, X/Twitter, Facebook
- Create Telegram Video Notes (circles)
- Extract MP3 audio from videos
- Generate thumbnails
- Trim videos
- Queue system for concurrent downloads
- Multi-language support (RU, UZ, EN)
- Download history
- SQLite database
- Docker support
- Temporary file cleanup

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

## Docker

```bash
docker-compose up --build
```

## Render

1. Push this repository to GitHub.
2. In Render, choose **New +** -> **Blueprint** and select the repository.
3. Set `BOT_TOKEN` in the Render environment settings.
4. Deploy the `mediasave-bot` web service.

The included `render.yaml` uses a free Web Service with a health endpoint. Free services
can sleep when idle, and their local SQLite data and temporary files are ephemeral.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | required |
| `DATABASE_URL` | Database URL | `sqlite:///mediasave.db` |
| `TEMP_DIR` | Temporary files directory | `./temp` |
| `MAX_FILE_SIZE_MB` | Max file size | `2000` |
| `MAX_QUEUE_SIZE` | Max queue size | `10` |
| `DOWNLOAD_TIMEOUT` | Download timeout (s) | `300` |
| `FFMPEG_TIMEOUT` | FFmpeg timeout (s) | `120` |
| `FFMPEG_PATH` | FFmpeg executable path | `ffmpeg` |
| `YOUTUBE_COOKIES_FILE` | Optional yt-dlp cookies file | empty |
| `YOUTUBE_COOKIES_BASE64` | Optional Base64 Netscape cookies for Render | empty |
| `LOG_LEVEL` | Logging level | `INFO` |
| `AUTO_DELETE_HOURS` | Auto-delete temp files after hours | `24` |
| `DEFAULT_LANGUAGE` | Default language | `ru` |

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
│   ├── database/
│   ├── services/
│   ├── i18n/
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
