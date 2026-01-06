"""
Система локализации бота.
Поддерживает русский и английский языки.
"""

from typing import Any
from bot.locales import ru, en


LANGUAGES = {
    'ru': ru.TEXTS,
    'en': en.TEXTS,
}

DEFAULT_LANGUAGE = 'ru'


def get_text(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: Any) -> str:
    """
    Получить локализованный текст по ключу.
    
    Args:
        key: Ключ текста (может быть вложенным через точку: "menu.tariffs")
        lang: Код языка (ru/en)
        **kwargs: Параметры для форматирования
        
    Returns:
        Локализованный текст
    """
    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    texts = LANGUAGES[lang]
    
    # Поддержка вложенных ключей через точку
    keys = key.split('.')
    value = texts
    
    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        # Если ключ не найден, пробуем в дефолтном языке
        if lang != DEFAULT_LANGUAGE:
            return get_text(key, DEFAULT_LANGUAGE, **kwargs)
        return f"[{key}]"
    
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value
    
    return value if isinstance(value, str) else f"[{key}]"


def get_language_name(lang: str) -> str:
    """Получить название языка."""
    names = {
        'ru': '🇷🇺 Русский',
        'en': '🇬🇧 English',
    }
    return names.get(lang, lang)


def get_available_languages() -> list[str]:
    """Получить список доступных языков."""
    return list(LANGUAGES.keys())
