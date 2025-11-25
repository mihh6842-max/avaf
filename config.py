"""
КОНФИГУРАЦИЯ БОТА
Централизованное хранение всех настроек с type hints
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Загружаем .env файл если существует
load_dotenv()

# === ТОКЕНЫ И КЛЮЧИ (ВАЖНО: не коммитить в Git!) ===
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8462258425:AAHk7pPanWzGWiD3aiJaR4qocguPaJDkfgo")
API_KEY: str = os.getenv("API_KEY", "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")
API_URL: str = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL: str = os.getenv("MODEL", "mistralai/mistral-7b-instruct")

# === ID АДМИНИСТРАТОРОВ ===
ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "1070125860,7338817463,6738709348")
ADMIN_IDS: List[int] = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

# === БОТ ТЕПЕРЬ ПОЛНОСТЬЮ БЕСПЛАТНЫЙ ===
# Настройки подписки и оплаты удалены - все функции доступны бесплатно

# Заглушки для обратной совместимости
YOOKASSA_SHOP_ID: str = ""
YOOKASSA_SECRET_KEY: str = ""

# === ФОРМУЛЫ РАСЧЕТА ===
FORMULAS: Dict[str, int] = {
    "deficit_calories": 300,  # Мягкий дефицит (было 500)
    "surplus_calories": 300,
    "calories_per_kg_fat": 7700
}

# === УРОВНИ АКТИВНОСТИ ===
ACTIVITY_LEVELS: Dict[str, float] = {
    "beginner": 1.375,
    "intermediate": 1.55,
    "advanced": 1.725
}

# === ЦЕЛЕВЫЕ КАЛОРИИ ===
TARGET_CALORIES: Dict[str, Any] = {
    "lose_weight": {"min": 1900, "max": 2000},
    "gain_muscle": {"min": 2600, "max": 2700},
    "maintain": 2400
}

# === СОСТОЯНИЯ РАЗГОВОРА ===
CONVERSATION_STATES: List[int] = list(range(9))
(LANGUAGE_SELECT, PROFILE_NAME, PROFILE_AGE, PROFILE_GENDER, PROFILE_HEIGHT,
 PROFILE_WEIGHT, PROFILE_GOAL, PROFILE_LEVEL, PROFILE_LIMITATIONS) = CONVERSATION_STATES

# === ПОДДЕРЖИВАЕМЫЕ ЯЗЫКИ ===
SUPPORTED_LANGUAGES: List[str] = ["ru", "en", "uz"]

# === ПУТИ К ДАННЫМ ===
DATABASE_PATH: str = 'data/fitness_bot.db'
WORKOUTS_PATH: str = 'book/workouts_by_level'
RECIPES_PATH: str = 'book'
