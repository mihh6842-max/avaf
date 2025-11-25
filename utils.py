"""
УТИЛИТЫ
Общие вспомогательные функции
"""

import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# Настройка логгера
logger = logging.getLogger(__name__)


def validate_age(age_str: str) -> Optional[int]:
    """
    Валидация возраста

    Args:
        age_str: Строка с возрастом

    Returns:
        int если валидно, None если нет
    """
    try:
        age = int(age_str)
        if 10 <= age <= 120:
            return age
        return None
    except (ValueError, TypeError):
        return None


def validate_weight(weight_str: str) -> Optional[float]:
    """
    Валидация веса

    Args:
        weight_str: Строка с весом

    Returns:
        float если валидно, None если нет
    """
    try:
        weight = float(weight_str.replace(',', '.'))
        if 30 <= weight <= 300:
            return weight
        return None
    except (ValueError, TypeError):
        return None


def validate_height(height_str: str) -> Optional[int]:
    """
    Валидация роста

    Args:
        height_str: Строка с ростом

    Returns:
        int если валидно, None если нет
    """
    try:
        height = int(height_str)
        if 100 <= height <= 250:
            return height
        return None
    except (ValueError, TypeError):
        return None


def parse_calories_from_text(text: str) -> int:
    """
    Извлечение калорий из текста

    Args:
        text: Текст с упоминанием калорий

    Returns:
        Количество калорий или 0 если не найдено
    """
    # Убираем все служебные символы
    text = re.sub(r'<\/?s>|BOS|EOS|/\*|\*/|###|\*\*|\*', '', text)

    # Ищем паттерны калорийности
    patterns = [
        r'[Ии]тогов[а-я]*\s*калорийност[ь]*[:\s]*(\d+)',
        r'[Ии]того[:\s]*(\d+)\s*ккал',
        r'[Вв]сего[:\s]*(\d+)\s*ккал',
        r'➡️[^:]*:\s*(\d+)\s*ккал',
        r'[Оо]бщ[а-я]*\s*калорийност[ь]*[:\s]*(\d+)',
        r'[Сс]умм[а-я]*[:\s]*(\d+)\s*ккал'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cal_value = int(match.group(1))
            # Проверка на адекватность (от 800 до 5000 ккал)
            if 800 <= cal_value <= 5000:
                return cal_value

    # Если не нашли итого, ищем все упоминания калорий
    all_cals = re.findall(r'(\d+)\s*ккал', text)
    if all_cals:
        # Преобразуем в числа и фильтруем
        cal_numbers = [int(cal) for cal in all_cals if 50 <= int(cal) <= 3000]

        if cal_numbers:
            # Если есть большое число (вероятно итоговое), берем его
            large_cals = [c for c in cal_numbers if c >= 1500]
            if large_cals:
                return max(large_cals)

            # Иначе суммируем все найденные калории
            total = sum(cal_numbers)
            if 800 <= total <= 5000:
                return total

    return 0


def clean_text(text: str) -> str:
    """
    Очистка текста от служебных символов

    Args:
        text: Исходный текст

    Returns:
        Очищенный текст
    """
    # Убираем BOS/EOS токены и другие артефакты
    patterns = [
        (r'<\|begin_of_text\|>', ''),
        (r'<\|end_of_text\|>', ''),
        (r'BOS', ''),
        (r'EOS', ''),
        (r'/\*.*?\*/', '', re.DOTALL),
        (r'###\s*', ''),
        (r'\*\*([^\*]+)\*\*', r'\1'),  # Убираем жирный шрифт но оставляем текст
        (r'\n{3,}', '\n\n'),  # Убираем множественные переносы
    ]

    for pattern, replacement, *flags in patterns:
        flag = flags[0] if flags else 0
        text = re.sub(pattern, replacement, text, flags=flag)

    return text.strip()


def format_number(number: float, decimals: int = 1) -> str:
    """
    Форматирование числа с округлением

    Args:
        number: Число для форматирования
        decimals: Количество знаков после запятой

    Returns:
        Отформатированная строка
    """
    return f"{number:.{decimals}f}"


def pluralize_ru(number: int, one: str, two: str, five: str) -> str:
    """
    Правильное склонение русских слов

    Args:
        number: Число
        one: Форма для 1 (упражнение)
        two: Форма для 2-4 (упражнения)
        five: Форма для 5+ (упражнений)

    Returns:
        Правильная форма слова
    """
    n = abs(number)
    n %= 100
    if 5 <= n <= 20:
        return five
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return two
    return five


def is_valid_telegram_user_id(user_id: Any) -> bool:
    """
    Проверка валидности Telegram user ID

    Args:
        user_id: ID пользователя

    Returns:
        True если валиден
    """
    try:
        user_id_int = int(user_id)
        # Telegram user ID всегда положительные и обычно от 1 до 10^10
        return 0 < user_id_int < 10**10
    except (ValueError, TypeError):
        return False


def safe_int(value: Any, default: int = 0) -> int:
    """
    Безопасное преобразование в int

    Args:
        value: Значение для преобразования
        default: Значение по умолчанию

    Returns:
        int значение или default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Безопасное преобразование в float

    Args:
        value: Значение для преобразования
        default: Значение по умолчанию

    Returns:
        float значение или default
    """
    try:
        return float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        return default


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Преобразование timestamp в datetime

    Args:
        timestamp: Unix timestamp

    Returns:
        datetime объект
    """
    try:
        return datetime.fromtimestamp(timestamp)
    except (ValueError, OSError):
        return datetime.now()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Разбивает список на чанки

    Args:
        lst: Исходный список
        chunk_size: Размер чанка

    Returns:
        Список списков
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
