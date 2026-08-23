import json
from pathlib import Path
from typing import Optional

I18N_DIR = Path(__file__).parent

_cache: dict[str, dict] = {}


def get_text(lang: str, key: str) -> str:
    if lang not in _cache:
        path = I18N_DIR / f"{lang}.json"
        if path.exists():
            _cache[lang] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _cache[lang] = {}
    return _cache.get(lang, {}).get(key, key)
