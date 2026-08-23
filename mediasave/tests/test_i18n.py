import pytest
from mediasave.app.i18n import get_text


def test_russian_texts():
    assert get_text("ru", "start_message") == "👋 Привет! Отправь мне ссылку на видео или изображение, и я попробую получить доступный медиафайл."
    assert get_text("ru", "menu_download") == "📥 Скачать"


def test_english_texts():
    assert get_text("en", "start_message") == "👋 Hi! Send me a link to a video or image, and I'll try to fetch the available media file."
    assert get_text("en", "menu_download") == "📥 Download"


def test_uzbek_texts():
    assert get_text("uz", "start_message") == "👋 Salom! Menga video yoki rasm havolasini yuboring, men mavjud media faylni olishga harakat qilaman."
    assert get_text("uz", "menu_download") == "📥 Yuklash"


def test_fallback_to_key():
    assert get_text("ru", "nonexistent_key") == "nonexistent_key"
