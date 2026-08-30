import asyncio
import aiohttp
import sys


async def check_telegram_connection():
    url = "https://api.telegram.org"
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                print(f"Telegram API reachable: {resp.status}")
                return True
    except Exception as e:
        print(f"Cannot reach Telegram API: {e}")
        return False


if __name__ == "__main__":
    ok = asyncio.run(check_telegram_connection())
    sys.exit(0 if ok else 1)
