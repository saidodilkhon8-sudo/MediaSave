import json
from pathlib import Path
from typing import Optional

_I18N: dict[str, dict[str, str]] = {}


def load_translations():
    i18n_dir = Path(__file__).resolve().parent
    for path in i18n_dir.glob("*.json"):
        lang = path.stem
        with open(path, "r", encoding="utf-8") as f:
            _I18N[lang] = json.load(f)


def get_text(lang: str, key: str, **kwargs) -> str:
    if not _I18N:
        load_translations()
    text = _I18N.get(lang, {}).get(key)
    if text is None:
        text = _I18N.get("en", {}).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
