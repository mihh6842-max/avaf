import os
import json
import logging
import asyncio
import re
import random
import hashlib
import time
import warnings
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import lru_cache
from collections import defaultdict
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, WebAppInfo
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler,
                         PreCheckoutQueryHandler, filters, ContextTypes, ConversationHandler)
from telegram.warnings import PTBUserWarning

# Suppress known PTB warnings about ConversationHandler
warnings.filterwarnings('ignore', category=PTBUserWarning)

# Визуальные улучшения
from visual_banners import visual_banners
from image_manager import image_manager

# Импорт интеллектуальной AI-системы
from intelligent_generator import IntelligentMealPlanner, IntelligentWorkoutPlanner, translate_with_ai
from quality_checker import QualityChecker
from recipes_loader import recipes_loader
from yookassa_handler import YooKassaHandler, store_pending_payment, get_pending_payment, remove_pending_payment

# Импорт новых систем (НОВАЯ СТРУКТУРА: 3015 упражнений по уровням!)
from workouts_loader_v4 import workouts_loader_v4 as workouts_loader
from database import db
from food_filter import food_filter
from calories_calculator import calories_calculator
from gamification import gamification, statistics

# Загрузка переводов
def load_translations():
    if os.path.exists("translations.json"):
        with open("translations.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

translations = load_translations()

def t(key: str, lang: str = "ru") -> str:
    """Получить перевод по ключу"""
    return translations.get(lang, {}).get(key, translations.get("ru", {}).get(key, key))

# Глобальная переменная для отслеживания языка в логах
_current_log_lang = "ru"

def set_log_lang(lang: str):
    """Установить язык для логирования"""
    global _current_log_lang
    _current_log_lang = lang

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ФУНКЦИЯ КРАСИВОЙ АНИМАЦИИ ====================

async def animated_loading(message, lang="ru"):
    """
    Красивая анимация генерации планов
    """
    animations_ru = [
        "🔄 Анализирую ваш профиль...",
        "🧠 Подбираю идеальные продукты...",
        "🍳 Создаю вкусные рецепты...",
        "📊 Рассчитываю калории и макросы...",
        "⚡ Оптимизирую план...",
        "✨ Финальные штрихи..."
    ]

    animations_en = [
        "🔄 Analyzing your profile...",
        "🧠 Selecting perfect products...",
        "🍳 Creating delicious recipes...",
        "📊 Calculating calories and macros...",
        "⚡ Optimizing the plan...",
        "✨ Final touches..."
    ]

    animations_uz = [
        "🔄 Profilingizni tahlil qilyapman...",
        "🧠 Ideal mahsulotlarni tanlayapman...",
        "🍳 Mazali retseptlar yaratyapman...",
        "📊 Kaloriya va makrolarni hisoblayapman...",
        "⚡ Rejani optimallashtirmoqda...",
        "✨ Yakuniy qo'shimchalar..."
    ]

    workout_animations_ru = [
        "🔄 Анализирую цели тренировки...",
        "💪 Подбираю упражнения...",
        "📋 Формирую программу...",
        "🎯 Настраиваю нагрузку...",
        "⚡ Оптимизирую тренировку...",
        "✨ Готово!"
    ]

    workout_animations_en = [
        "🔄 Analyzing workout goals...",
        "💪 Selecting exercises...",
        "📋 Creating program...",
        "🎯 Adjusting intensity...",
        "⚡ Optimizing workout...",
        "✨ Done!"
    ]

    workout_animations_uz = [
        "🔄 Mashg'ulot maqsadlarini tahlil qilmoqda...",
        "💪 Mashqlarni tanlayapman...",
        "📋 Dastur yaratyapman...",
        "🎯 Yukni sozlayapman...",
        "⚡ Mashg'ulotni optimallashtirmoqda...",
        "✨ Tayyor!"
    ]

    # Выбираем набор анимаций
    animations = animations_ru
    if lang == "en":
        animations = animations_en
    elif lang == "uz":
        animations = animations_uz

    # Проходим по всем этапам
    import asyncio
    for step in animations:
        try:
            await message.edit_text(step)
            await asyncio.sleep(0.6)  # Пауза между этапами
        except Exception as e:
            # Игнорируем ошибки редактирования (если сообщение не изменилось)
            pass

    return message

async def animated_workout_loading(message, lang="ru"):
    """
    Анимация для планов тренировок
    """
    animations_ru = [
        "🔄 Анализирую цели тренировки...",
        "💪 Подбираю упражнения...",
        "📋 Формирую программу...",
        "🎯 Настраиваю нагрузку...",
        "⚡ Оптимизирую тренировку...",
        "✨ Готово!"
    ]

    animations_en = [
        "🔄 Analyzing workout goals...",
        "💪 Selecting exercises...",
        "📋 Creating program...",
        "🎯 Adjusting intensity...",
        "⚡ Optimizing workout...",
        "✨ Done!"
    ]

    animations_uz = [
        "🔄 Mashg'ulot maqsadlarini tahlil qilmoqda...",
        "💪 Mashqlarni tanlayapman...",
        "📋 Dastur yaratyapman...",
        "🎯 Yukni sozlayapman...",
        "⚡ Mashg'ulotni optimallashtirmoqda...",
        "✨ Tayyor!"
    ]

    animations = animations_ru
    if lang == "en":
        animations = animations_en
    elif lang == "uz":
        animations = animations_uz

    import asyncio
    for step in animations:
        try:
            await message.edit_text(step)
            await asyncio.sleep(0.6)
        except Exception as e:
            pass

    return message

# Импортируем конфиг
try:
    from config import BOT_TOKEN, API_KEY, API_URL, MODEL
except ImportError:
    # Если config.py не найден, используем значения по умолчанию (для обратной совместимости)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    API_KEY = os.getenv("API_KEY", "")
    API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
    MODEL = os.getenv("MODEL", "mistralai/mistral-7b-instruct")

# Импортируем ADMIN_IDS из конфига
try:
    from config import ADMIN_IDS
except ImportError:
    ADMIN_IDS = [1070125860, 7338817463]

(LANGUAGE_SELECT, PROFILE_NAME, PROFILE_AGE, PROFILE_GENDER, PROFILE_HEIGHT, PROFILE_WEIGHT,
 PROFILE_GOAL, PROFILE_LEVEL, PROFILE_LIMITATIONS) = range(9)

class Settings:
    def __init__(self):
        self.data = self.load()
    
    def load(self):
        if os.path.exists("settings.json"):
            with open("settings.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "formulas": {
                "deficit_calories": 500,
                "surplus_calories": 500,
                "calories_per_kg_fat": 7700
            },
            "activity_levels": {
                "beginner": 1.375,
                "intermediate": 1.55,
                "advanced": 1.725
            },
            "target_calories": {
                "lose_weight": {"min": 1900, "max": 2000},
                "gain_muscle": {"min": 2600, "max": 2700},
                "maintain": 2400
            }
        }
    
    def save(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_prompts(self):
        if os.path.exists("prompts.json"):
            with open("prompts.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

settings = Settings()

# БОТ ПОЛНОСТЬЮ БЕСПЛАТНЫЙ - код подписок удален

class Database:
    def __init__(self, filename="database.json"):
        self.filename = filename
        self.data = self._load()
        self._save_pending = False
        self._last_save_time = time.time()
        self._save_interval = 5  # Сохранять не чаще чем раз в 5 секунд

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки БД: {e}")
                # Создаем бэкап поврежденной БД
                if os.path.exists(self.filename):
                    backup_name = f"{self.filename}.backup.{int(time.time())}"
                    os.rename(self.filename, backup_name)
                    logger.info(f"Создан бэкап поврежденной БД: {backup_name}")
        return {"users": {}, "stats": {"total_users": 0, "active_subscriptions": 0}}

    def _save(self, force=False):
        """Сохранение с умным интервалом"""
        current_time = time.time()

        # Если не прошло достаточно времени и не форсируется - отложить
        if not force and (current_time - self._last_save_time) < self._save_interval:
            self._save_pending = True
            return

        try:
            # Атомарная запись через временный файл
            temp_file = f"{self.filename}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

            # Заменяем старый файл новым
            if os.path.exists(self.filename):
                os.replace(temp_file, self.filename)
            else:
                os.rename(temp_file, self.filename)

            self._last_save_time = current_time
            self._save_pending = False
        except Exception as e:
            logger.error(f"Ошибка сохранения БД: {e}")

    def save_if_pending(self):
        """Сохранить если есть отложенные изменения"""
        if self._save_pending:
            self._save(force=True)
    
    def get_user(self, user_id: int):
        return self.data["users"].get(str(user_id))
    
    def create_user(self, user_id: int, username: str = None):
        user_data = {
            "user_id": user_id,
            "username": username,
            "registration_date": datetime.now().isoformat(),
            "profile": {},
            "language": None,
            "referral_code": f"REF{user_id}",
            "referred_by": None,
            "current_training_day": 1,
            "training_history": [],
            "daily_results": [],
            "last_free_tip": None,
            "chat_mode": False,
            "chat_history": []
        }
        self.data["users"][str(user_id)] = user_data
        self.data["stats"]["total_users"] += 1
        self._save()
        return user_data
    
    def update_user(self, user_id: int, updates: Dict):
        user_str = str(user_id)
        if user_str in self.data["users"]:
            self.data["users"][user_str].update(updates)
            self._save()
    
    def has_active_subscription(self, user_id: int):
        # БОТ ТЕПЕРЬ ПОЛНОСТЬЮ БЕСПЛАТНЫЙ - ВСЕ ФУНКЦИИ ДОСТУПНЫ ВСЕМ
        return True
    
    def add_subscription(self, user_id: int, days: int):
        user = self.get_user(user_id)
        if not user:
            return
        now = datetime.now()
        current_end = now
        if user.get("subscription_end"):
            sub_end = datetime.fromisoformat(user["subscription_end"])
            if sub_end > now:
                current_end = sub_end
        new_end = current_end + timedelta(days=days)
        self.update_user(user_id, {"subscription_end": new_end.isoformat()})
    
    def get_stats(self):
        active_subs = sum(1 for user in self.data["users"].values() 
                         if self.has_active_subscription(int(user["user_id"])))
        self.data["stats"]["active_subscriptions"] = active_subs
        return self.data["stats"]

db = Database()

def check_and_award_achievements(user_id: int, action_type: str = None):
    """
    Проверяет и начисляет достижения пользователю
    action_type: 'workout', 'nutrition', 'water_goal'
    """
    user = db.get_user(user_id)
    if not user:
        return None

    lang = user.get("language", "ru")

    # Инициализация если нужно
    if "achievements" not in user:
        user["achievements"] = []
    if "stats" not in user:
        user["stats"] = {"workouts": 0, "nutrition_plans": 0, "days_streak": 0, "water_days": 0}

    achievements = user["achievements"]
    stats = user["stats"]
    new_achievement = None

    # Обновляем статистику
    if action_type == "workout":
        stats["workouts"] = stats.get("workouts", 0) + 1

        # Первая тренировка
        if stats["workouts"] == 1 and "first_workout" not in achievements:
            achievements.append("first_workout")
            new_achievement = "achievement_first_workout"

        # 10 тренировок
        elif stats["workouts"] == 10 and "10_workouts" not in achievements:
            achievements.append("10_workouts")
            new_achievement = "achievement_10_workouts"

        # 50 тренировок
        elif stats["workouts"] == 50 and "50_workouts" not in achievements:
            achievements.append("50_workouts")
            new_achievement = "achievement_50_workouts"

    elif action_type == "nutrition":
        stats["nutrition_plans"] = stats.get("nutrition_plans", 0) + 1

    elif action_type == "water_goal":
        stats["water_days"] = stats.get("water_days", 0) + 1

        # Достижение за воду
        if "water_goal" not in achievements:
            achievements.append("water_goal")
            new_achievement = "achievement_water_goal"

    # Сохраняем обновления
    user["achievements"] = achievements
    user["stats"] = stats
    db.update_user(user_id, user)

    # Возвращаем сообщение о новом достижении
    if new_achievement:
        return t("achievement_unlocked", lang).format(achievement=t(new_achievement, lang))

    return None

def calculate_calories(profile: Dict):
    weight = profile.get("weight", 70)
    height = profile.get("height", 170)
    age = profile.get("age", 30)
    gender = profile.get("gender", "male")
    goal = profile.get("goal", "maintain")
    level = profile.get("level", "intermediate")
    
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    activity_multiplier = settings.data["activity_levels"].get(level, 1.55)
    tdee = bmr * activity_multiplier
    
    # Рассчитываем калории на основе цели
    if goal == "lose_weight":
        daily_calories = int(tdee - 300)  # Мягкий дефицит 300 ккал (было 500)
    elif goal == "gain_muscle":
        daily_calories = int(tdee + 300)  # Профицит 300 ккал для набора
    else:
        daily_calories = int(tdee)  # Поддержание веса
    
    calorie_diff = abs(tdee - daily_calories)
    weekly_change = (calorie_diff * 7) / settings.data["formulas"]["calories_per_kg_fat"]
    
    ideal_weight_range = f"{round(18.5 * (height/100)**2, 1)}-{round(24.9 * (height/100)**2, 1)} кг"
    
    return {
        "daily_calories": daily_calories,
        "bmr": round(bmr),
        "tdee": round(tdee),
        "weekly_change": round(weekly_change, 2),
        "ideal_weight_range": ideal_weight_range,
        "protein_g": round(weight * 2.0, 1),
        "fats_g": round(weight * 1.0, 1),
        "carbs_g": round((daily_calories - (weight * 2.0 * 4) - (weight * 1.0 * 9)) / 4, 1)
    }

def calculate_workout_calories(weight: float, duration: str, intensity: str):
    met_values = {
        "high": 6.0,
        "medium": 5.0,
        "low": 4.0,
        "recovery": 3.0
    }
    
    duration_hours = {"30 минут": 0.5, "45-60 минут": 0.875, "1.5 часа": 1.5}.get(duration, 0.875)
    met = met_values.get(intensity, 5.0)
    
    return round(met * weight * duration_hours)

def parse_calories_from_text(text: str) -> int:
    """Парсит калорийность из текста плана питания"""
    import re
    
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

def parse_workout_calories(text: str) -> int:
    """Парсит сожженные калории из текста тренировки"""
    import re
    
    # Убираем служебные символы
    text = re.sub(r'<\/?s>|BOS|EOS|/\*|\*/|###|\*\*|\*', '', text)
    
    patterns = [
        r'[Рр]асход\s*калорий[:\s]*~?(\d+)',
        r'[Сс]ожжено[:\s]*~?(\d+)',
        r'🔥[^:]*:\s*~?(\d+)\s*ккал',
        r'🔥\s*~?(\d+)\s*ккал',  # Формат: 🔥 ~270 ккал
        r'[Пп]отрачено[:\s]*~?(\d+)',
        r'[Зз]атрачено[:\s]*~?(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cal_value = int(match.group(1))
            # Проверка на адекватность (от 50 до 2000 ккал)
            if 50 <= cal_value <= 2000:
                return cal_value
    
    return 0

def save_daily_results(user_id: int, nutrition_cals: int, workout_cals: int):
    """Сохраняет результаты дня"""
    user = db.get_user(user_id)
    if not user:
        return
    
    daily_results = user.get("daily_results", [])
    
    # Проверяем, есть ли уже запись за сегодня
    today = datetime.now().date()
    today_result = None
    for result in daily_results:
        result_date = datetime.fromisoformat(result["date"]).date()
        if result_date == today:
            today_result = result
            break
    
    if today_result:
        # Обновляем существующую запись
        today_result["nutrition_calories"] = nutrition_cals
        today_result["workout_calories"] = workout_cals
        today_result["net_calories"] = nutrition_cals - workout_cals
    else:
        # Добавляем новую запись
        result = {
            "date": datetime.now().isoformat(),
            "nutrition_calories": nutrition_cals,
            "workout_calories": workout_cals,
            "net_calories": nutrition_cals - workout_cals
        }
        daily_results.append(result)
    
    # Храним только последние 90 дней
    if len(daily_results) > 90:
        daily_results = daily_results[-90:]
    
    db.update_user(user_id, {"daily_results": daily_results})

def calculate_weight_loss_progress(user_id: int) -> dict:
    """Рассчитывает прогресс потери/набора веса по неделям"""
    user = db.get_user(user_id)
    if not user:
        return {"weeks": [], "total_change": 0}
    
    daily_results = user.get("daily_results", [])
    if not daily_results:
        return {"weeks": [], "total_change": 0}
    
    # Группируем по неделям
    from collections import defaultdict
    weeks_data = defaultdict(list)
    
    for result in daily_results:
        result_date = datetime.fromisoformat(result["date"])
        # Определяем номер недели
        week_number = result_date.isocalendar()[1]
        year = result_date.year
        week_key = f"{year}-W{week_number}"
        weeks_data[week_key].append(result)
    
    # Рассчитываем изменение веса для каждой недели
    weekly_changes = []
    for week_key in sorted(weeks_data.keys()):
        week_results = weeks_data[week_key]
        total_deficit = sum(r.get("net_calories", 0) for r in week_results)
        # 7700 ккал = 1 кг жира
        weight_change = -total_deficit / settings.data["formulas"]["calories_per_kg_fat"]
        weekly_changes.append({
            "week": week_key,
            "deficit": total_deficit,
            "weight_change": round(weight_change, 2),
            "days": len(week_results)
        })
    
    total_change = sum(w["weight_change"] for w in weekly_changes)
    
    return {
        "weeks": weekly_changes,
        "total_change": round(total_change, 2)
    }

def validate_ai_response(text: str, response_type: str = "nutrition") -> dict:
    """
    Проверяет качество ответа от AI
    Возвращает: {"valid": bool, "reason": str, "text": str}
    """
    import re

    # Убираем служебные символы
    clean_text = re.sub(r'<\/?s>|BOS|EOS|/\*|\*/|###|\*\*|\*', '', text).strip()

    # ПРОВЕРКИ УБРАНЫ - просто возвращаем валидный результат
    return {
        "valid": True,
        "reason": "",
        "text": clean_text
    }

    # Проверка 2: УБРАНА - теперь работает для всех языков

    # Проверка 3: Для планов питания - мультиязычная проверка
    if response_type == "nutrition":
        # Ключевые слова на всех языках
        nutrition_keywords_multi = [
            # Русский
            'завтрак', 'обед', 'ужин', 'перекус', 'ккал', 'грамм', 'рецепт', 'калори',
            # English
            'breakfast', 'lunch', 'dinner', 'snack', 'kcal', 'calories', 'recipe', 'meal',
            # Uzbek
            'nonushta', 'tushlik', 'kechki', 'gazak', 'kkal', 'retsept', 'ovqat'
        ]
        found_keywords = sum(1 for kw in nutrition_keywords_multi if kw.lower() in clean_text.lower())

        # Проверка наличия калорий в любом формате
        has_calories = bool(re.search(r'(\d+)\s*(ккал|kcal|kkal|calories)', clean_text, re.IGNORECASE))

        # Если есть хотя бы 2 ключевых слова ИЛИ информация о калориях - OK
        if found_keywords < 2 and not has_calories:
            return {
                "valid": False,
                "reason": "План питания не содержит достаточно информации",
                "text": clean_text
            }

    # Проверка 4: Для тренировок - мультиязычная проверка
    if response_type == "workout":
        workout_keywords_multi = [
            # Русский
            'упражнение', 'подход', 'повторени', 'разминка', 'заминка', 'тренировка', 'сет',
            # English
            'exercise', 'set', 'rep', 'workout', 'warm', 'cool', 'training',
            # Uzbek
            'mashq', 'takror', 'issiq', 'mashg\'ulot', 'trening'
        ]
        found_keywords = sum(1 for kw in workout_keywords_multi if kw.lower() in clean_text.lower())

        # Достаточно 1-2 ключевых слов
        if found_keywords < 1:
            return {
                "valid": False,
                "reason": "План тренировки не содержит достаточно информации",
                "text": clean_text
            }
    
    # Проверка 5: Проверка на "битые" ответы (много повторений)
    words = clean_text.split()
    if len(words) > 10:
        # Проверяем на повторяющиеся последовательности
        for i in range(len(words) - 5):
            pattern = ' '.join(words[i:i+5])
            occurrences = clean_text.count(pattern)
            if occurrences > 3:
                return {
                    "valid": False,
                    "reason": "Ответ содержит повторяющиеся фрагменты",
                    "text": clean_text
                }
    
    return {"valid": True, "reason": "OK", "text": clean_text}

def final_clean_text(text: str) -> str:
    """
    Финальная очистка текста от всех нежелательных символов перед отправкой пользователю
    МАКСИМАЛЬНО сохраняя оригинальное форматирование
    """
    import re
    
    # Шаг 1: Удаляем только запрещенные спецсимволы
    forbidden_patterns = [
        r'\*\*',      # Двойные звездочки
        r'\*',        # Одинарные звездочки
        r'###',       # Решетки
        r'<\/?s>',    # Теги <s> и </s>
        r'BOS',       # BOS
        r'EOS',       # EOS
        r'/\*',       # Начало комментария
        r'\*/',       # Конец комментария
        r'\[',        # Открывающая скобка
        r'\]',        # Закрывающая скобка
        r'\(',        # Открывающая круглая скобка
        r'\)',        # Закрывающая круглая скобка
        r'/OUT',      # Технический маркер
        r'OUT',       # Технический маркер
    ]
    
    cleaned = text
    for pattern in forbidden_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Шаг 2: Построчная очистка лишних пробелов
    lines = cleaned.split('\n')
    processed_lines = []
    
    for line in lines:
        # Убираем пробелы в начале и конце строки
        line = line.strip()
        # Заменяем множественные пробелы на один
        line = re.sub(r' {2,}', ' ', line)
        processed_lines.append(line)
    
    cleaned = '\n'.join(processed_lines)
    
    # Шаг 3: Нормализуем пустые строки (не более 2 подряд)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Шаг 4: Финальная очистка краёв
    cleaned = cleaned.strip()
    
    return cleaned
    """
    Финальная очистка текста от всех нежелательных символов перед отправкой пользователю
    СОХРАНЯЯ оригинальное форматирование и переносы строк
    """
    # Удаляем все спецсимволы и форматирование, НО сохраняем переносы строк
    cleaned = re.sub(r'\*\*|\*|###|<\/?s>|BOS|EOS|/\*|\*/|\[|\]|\(|\)', '', text)
    
    # Удаляем множественные пробелы НА ОДНОЙ СТРОКЕ (не трогая \n)
    lines = cleaned.split('\n')
    cleaned_lines = []
    for line in lines:
        # Убираем лишние пробелы внутри строки
        cleaned_line = re.sub(r' {2,}', ' ', line.strip())
        cleaned_lines.append(cleaned_line)
    
    cleaned = '\n'.join(cleaned_lines)
    
    # Удаляем множественные переводы строк (больше 2 подряд)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Убираем пробелы в начале и конце всего текста
    cleaned = cleaned.strip()
    
    return cleaned

# ==================== СИСТЕМА КЭШИРОВАНИЯ И RATE LIMITING ====================

class AICache:
    """Система кэширования AI запросов для экономии API лимитов"""
    def __init__(self, cache_file="ai_cache.json", ttl_hours=24):
        self.cache_file = cache_file
        self.ttl_seconds = ttl_hours * 3600
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _get_cache_key(self, prompt: str, system_prompt: str = None):
        """Генерирует уникальный ключ для кэша"""
        content = f"{system_prompt or ''}{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, system_prompt: str = None):
        """Получить из кэша"""
        key = self._get_cache_key(prompt, system_prompt)
        if key in self.cache:
            cached = self.cache[key]
            # Проверяем не устарел ли кэш
            if time.time() - cached['timestamp'] < self.ttl_seconds:
                logger.info("✅ Ответ получен из кэша (экономия API лимита)")
                return cached['response']
            else:
                # Удаляем устаревший кэш
                del self.cache[key]
        return None

    def set(self, prompt: str, system_prompt: str, response: str):
        """Сохранить в кэш"""
        key = self._get_cache_key(prompt, system_prompt)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        self._save_cache()

    def clear_old(self):
        """Очистить устаревший кэш"""
        current_time = time.time()
        keys_to_delete = []
        for key, value in self.cache.items():
            if current_time - value['timestamp'] > self.ttl_seconds:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.cache[key]

        if keys_to_delete:
            self._save_cache()
            logger.info(f"🧹 Очищено {len(keys_to_delete)} устаревших записей кэша")

class RateLimiter:
    """Rate limiter для предотвращения превышения API лимитов"""
    def __init__(self, max_requests_per_minute=10, max_requests_per_hour=50):
        self.max_per_minute = max_requests_per_minute
        self.max_per_hour = max_requests_per_hour
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)

    def _clean_old_requests(self, user_id: int):
        """Очистить старые запросы"""
        current_time = time.time()

        # Очистка минутных запросов
        self.minute_requests[user_id] = [
            req_time for req_time in self.minute_requests[user_id]
            if current_time - req_time < 60
        ]

        # Очистка часовых запросов
        self.hour_requests[user_id] = [
            req_time for req_time in self.hour_requests[user_id]
            if current_time - req_time < 3600
        ]

    def can_make_request(self, user_id: int) -> tuple[bool, str]:
        """Проверить можно ли сделать запрос"""
        self._clean_old_requests(user_id)

        # Проверка минутного лимита
        if len(self.minute_requests[user_id]) >= self.max_per_minute:
            return False, "Слишком много запросов. Подождите минуту."

        # Проверка часового лимита
        if len(self.hour_requests[user_id]) >= self.max_per_hour:
            return False, "Достигнут часовой лимит запросов. Попробуйте позже."

        return True, ""

    def add_request(self, user_id: int):
        """Зарегистрировать запрос"""
        current_time = time.time()
        self.minute_requests[user_id].append(current_time)
        self.hour_requests[user_id].append(current_time)

# Инициализация систем
ai_cache = AICache()
rate_limiter = RateLimiter()

# ==================== КОНЕЦ СИСТЕМ КЭШИРОВАНИЯ ====================

class AIGenerator:
    """
    ИНТЕЛЛЕКТУАЛЬНАЯ СИСТЕМА ГЕНЕРАЦИИ ПЛАНОВ
    Работает БЕЗ внешних API - использует локальную базу знаний
    """

    # Инициализируем интеллектуальные системы
    meal_planner = IntelligentMealPlanner()
    workout_planner = IntelligentWorkoutPlanner()
    quality_checker = QualityChecker()

    @staticmethod
    def _pluralize_ru(number: int, one: str, two: str, five: str) -> str:
        """Правильное склонение русских слов (1 упражнение, 2 упражнения, 5 упражнений)"""
        n = abs(number)
        n %= 100
        if n >= 5 and n <= 20:
            return five
        n %= 10
        if n == 1:
            return one
        if n >= 2 and n <= 4:
            return two
        return five

    @staticmethod
    def generate_nutrition_plan(profile: Dict, preferences: Dict, lang: str = "ru", user_id: int = None):
        """Генерирует план питания из базы рецептов (book/)"""

        if user_id:
            user = db.get_user(user_id)
            if user:
                lang = user.get("language", "ru")

        logger.info("Создание плана питания...")

        try:
            # Определяем цель пользователя
            goal = profile.get('goal', 'maintain')

            # Получаем продукты пользователя
            available_products = preferences.get('available_products', '')
            if available_products:
                user_ingredients = [ing.strip() for ing in available_products.split(',')]

                # Если язык не русский, переводим продукты на русский для поиска
                if lang and lang != "ru":
                    try:
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source=lang, target='ru')
                        translated_ingredients = []
                        for ing in user_ingredients:
                            try:
                                translated = translator.translate(ing)
                                translated_ingredients.append(translated if translated else ing)
                                logger.info(f"Translated ingredient: {ing} → {translated}")
                            except:
                                translated_ingredients.append(ing)
                        user_ingredients = translated_ingredients
                    except Exception as e:
                        logger.warning(f"Failed to translate ingredients: {e}")
            else:
                user_ingredients = []

            # Получаем рецепты для каждого приема пищи
            if user_ingredients:
                breakfast_list = recipes_loader.search_by_ingredients(goal, "завтрак", user_ingredients)
                lunch_list = recipes_loader.search_by_ingredients(goal, "обед", user_ingredients)
                dinner_list = recipes_loader.search_by_ingredients(goal, "ужин", user_ingredients)
            else:
                # Получаем больше рецептов для разнообразия
                breakfast_list = recipes_loader.get_recipes(goal, "завтрак", 10)
                lunch_list = recipes_loader.get_recipes(goal, "обед", 10)
                dinner_list = recipes_loader.get_recipes(goal, "ужин", 10)

            # Выбираем СЛУЧАЙНЫЕ рецепты для разнообразия
            breakfast = random.choice(breakfast_list) if breakfast_list else recipes_loader.get_recipe("maintain", "завтрак")
            lunch = random.choice(lunch_list) if lunch_list else recipes_loader.get_recipe("maintain", "обед")
            dinner = random.choice(dinner_list) if dinner_list else recipes_loader.get_recipe("maintain", "ужин")

            # Проверяем что рецепты найдены
            if not breakfast or not lunch or not dinner:
                logger.error(f"Рецепты не найдены: breakfast={breakfast is not None}, lunch={lunch is not None}, dinner={dinner is not None}")
                return "❌ Ошибка: не удалось найти рецепты. Попробуйте указать другие продукты."

            # Получаем БЖУ напрямую из рецепта
            breakfast_bju = {
                'protein': int(breakfast.get('protein', 0)),
                'fat': int(breakfast.get('fats', 0)),
                'carbs': int(breakfast.get('carbs', 0))
            }
            lunch_bju = {
                'protein': int(lunch.get('protein', 0)),
                'fat': int(lunch.get('fats', 0)),
                'carbs': int(lunch.get('carbs', 0))
            }
            dinner_bju = {
                'protein': int(dinner.get('protein', 0)),
                'fat': int(dinner.get('fats', 0)),
                'carbs': int(dinner.get('carbs', 0))
            }

            breakfast_cals = int(breakfast.get('calories', 0))
            lunch_cals = int(lunch.get('calories', 0))
            dinner_cals = int(dinner.get('calories', 0))

            # Формируем план
            plan = "═══════════════════════════\n"
            plan += "🍽  ПЕРСОНАЛЬНЫЙ ПЛАН ПИТАНИЯ\n"
            plan += "═══════════════════════════\n\n"

            # ЗАВТРАК
            plan += "🌅  ЗАВТРАК\n"
            plan += "─────────────────────────\n"
            plan += f"🍳  {breakfast['Название блюда']}\n\n"
            plan += "📦  Ингредиенты:\n"
            for ing in breakfast['Ингредиенты']:
                plan += f"   • {ing}\n"
            plan += f"\n👨‍🍳  Приготовление:\n   {breakfast['Приготовление']}\n\n"
            plan += f"📊  Пищевая ценность:\n"
            plan += f"   🔥 Калории: {breakfast_cals} ккал\n"
            plan += f"   💪 Белки: {breakfast_bju['protein']}г  |  🥑 Жиры: {breakfast_bju['fat']}г  |  🍞 Углеводы: {breakfast_bju['carbs']}г\n\n"

            # ОБЕД
            plan += "🌞  ОБЕД\n"
            plan += "─────────────────────────\n"
            plan += f"🍳  {lunch['Название блюда']}\n\n"
            plan += "📦  Ингредиенты:\n"
            for ing in lunch['Ингредиенты']:
                plan += f"   • {ing}\n"
            plan += f"\n👨‍🍳  Приготовление:\n   {lunch['Приготовление']}\n\n"
            plan += f"📊  Пищевая ценность:\n"
            plan += f"   🔥 Калории: {lunch_cals} ккал\n"
            plan += f"   💪 Белки: {lunch_bju['protein']}г  |  🥑 Жиры: {lunch_bju['fat']}г  |  🍞 Углеводы: {lunch_bju['carbs']}г\n\n"

            # УЖИН
            plan += "🌙  УЖИН\n"
            plan += "─────────────────────────\n"
            plan += f"🍳  {dinner['Название блюда']}\n\n"
            plan += "📦  Ингредиенты:\n"
            for ing in dinner['Ингредиенты']:
                plan += f"   • {ing}\n"
            plan += f"\n👨‍🍳  Приготовление:\n   {dinner['Приготовление']}\n\n"
            plan += f"📊  Пищевая ценность:\n"
            plan += f"   🔥 Калории: {dinner_cals} ккал\n"
            plan += f"   💪 Белки: {dinner_bju['protein']}г  |  🥑 Жиры: {dinner_bju['fat']}г  |  🍞 Углеводы: {dinner_bju['carbs']}г\n\n"

            total_cals = breakfast_cals + lunch_cals + dinner_cals
            total_protein = breakfast_bju['protein'] + lunch_bju['protein'] + dinner_bju['protein']
            total_fat = breakfast_bju['fat'] + lunch_bju['fat'] + dinner_bju['fat']
            total_carbs = breakfast_bju['carbs'] + lunch_bju['carbs'] + dinner_bju['carbs']

            # Рассчитываем целевые калории
            calories_info = calculate_calories(profile)
            target_cals = calories_info['daily_calories']

            plan += "═══════════════════════════\n"
            plan += "📊  ИТОГО ЗА ДЕНЬ\n"
            plan += "═══════════════════════════\n"
            plan += f"🔥  Калории: {total_cals} ккал (цель: {target_cals} ккал)\n"
            plan += f"💪  Белки: {total_protein}г  |  🥑  Жиры: {total_fat}г  |  🍞  Углеводы: {total_carbs}г\n\n"

            plan += "🔥  Ваш метаболизм:\n"
            plan += f"   • BMR: {calories_info['bmr']} ккал/день\n"
            plan += f"   • TDEE: {calories_info['tdee']} ккал/день\n\n"

            weight = profile.get('weight', 70)
            plan += f"💧  Вода: {round(weight * 0.03, 1)}L в день\n\n"

            # Прогноз изменения веса
            cal_diff = calories_info['tdee'] - total_cals
            weekly_change = (cal_diff * 7) / 7700

            if goal == 'lose_weight':
                plan += f"📉  Прогноз похудения: -{abs(weekly_change):.2f} кг/неделю\n\n"
            elif goal == 'gain_muscle':
                plan += f"📈  Прогноз набора: +{abs(weekly_change):.2f} кг/неделю\n\n"
            else:
                plan += f"⚖️  Прогноз: Поддержание веса\n\n"

            plan += "💡  Совет: Следуйте плану для достижения результатов!\n\n"
            plan += "🍽  Приятного аппетита!\n"

            # Генерируем HTML-версию плана (упрощенная версия)
            try:
                import time

                # Создаем простой HTML без сложного парсинга
                plans_dir = os.path.join('static', 'plans')
                os.makedirs(plans_dir, exist_ok=True)

                timestamp = str(int(time.time()))
                filename = f'plan_{user_id}_{timestamp}.html'
                filepath = os.path.join(plans_dir, filename)

                # Читаем шаблон
                template_path = os.path.join('templates', 'plan_style_colorful.html')
                with open(template_path, 'r', encoding='utf-8') as f:
                    html = f.read()

                # Простая замена данных
                html = html.replace('1955', str(total_cals))
                html = html.replace('2272', str(target_cals))
                html = html.replace('82г</div>', f'{total_protein}г</div>')
                html = html.replace('80г</div>', f'{total_fat}г</div>')
                html = html.replace('185г</div>', f'{total_carbs}г</div>')
                html = html.replace('1273', str(calories_info['bmr']))
                html = html.replace('1973', str(calories_info['tdee']))

                # Добавляем мета-тег для Telegram Web App
                html = html.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">')

                # Сохраняем
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)

                # Сохраняем путь к HTML
                if user_id:
                    user = db.get_user(user_id)
                    if user:
                        user['last_plan_html'] = filepath
                        user['last_plan_content'] = html  # Сохраняем контент для inline отправки
                        db.update_user(user_id, user)

                logger.info(f"HTML план сохранен: {filepath}")

                # Автозагрузка на Netlify
                try:
                    import requests as req
                    import base64

                    # Netlify настройки
                    NETLIFY_SITE_ID = "charming-longma-524d08"  # Из URL
                    NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN", "")  # Создай токен

                    if NETLIFY_TOKEN:
                        filename = os.path.basename(filepath)

                        # Читаем файл в base64
                        with open(filepath, 'rb') as f:
                            file_content = base64.b64encode(f.read()).decode()

                        # Netlify API для добавления файла
                        deploy_url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"

                        headers = {
                            "Authorization": f"Bearer {NETLIFY_TOKEN}",
                            "Content-Type": "application/json"
                        }

                        deploy_data = {
                            "files": {
                                f"plans/{filename}": file_content
                            }
                        }

                        resp = req.post(deploy_url, headers=headers, json=deploy_data, timeout=30)

                        if resp.status_code in [200, 201]:
                            logger.info(f"✅ План загружен на Netlify: plans/{filename}")
                        else:
                            logger.warning(f"⚠️ Netlify деплой не удался: {resp.status_code}")
                    else:
                        logger.info("ℹ️ NETLIFY_TOKEN не настроен - автозагрузка отключена")

                except Exception as e:
                    logger.warning(f"⚠️ Ошибка автозагрузки на Netlify: {e}")

            except Exception as e:
                logger.error(f"Ошибка генерации HTML плана: {e}")
                # Не критично, продолжаем работу

            # AI-перевод если язык != ru
            if lang and lang != "ru":
                plan = translate_with_ai(plan, lang)

            logger.info("План питания создан")
            return plan

        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            import traceback
            traceback.print_exc()
            return "❌ Ошибка создания плана питания. Попробуйте ещё раз."

    @staticmethod
    def generate_workout_plan(profile: Dict, workout_info: Dict, user_id: int = None):
        """
        УЛУЧШЕННАЯ генерация плана тренировки
        - Адаптация под место (дома БЕЗ инвентаря)
        - Точный расчет упражнений по времени
        - Учет уровня усталости
        - Прогрессия по уровню подготовки
        """

        # Определяем язык пользователя
        lang = "ru"
        if user_id:
            user = db.get_user(user_id)
            if user:
                lang = user.get("language", "ru")
                set_log_lang(lang)

        logger.info("🧠 Генерация УЛУЧШЕННОГО плана тренировки...")

        try:
            # 1. ОПРЕДЕЛЯЕМ ПАРАМЕТРЫ
            goal = profile.get('goal', 'maintain')
            goal_map = {
                'lose': 'lose_weight',
                'lose_weight': 'lose_weight',
                'gain': 'gain_weight',
                'gain_muscle': 'gain_weight',
                'gain_weight': 'gain_weight',
                'maintain': 'maintain_weight',
                'maintain_weight': 'maintain_weight'
            }
            goal = goal_map.get(goal, 'maintain_weight')

            # 2. ОПРЕДЕЛЯЕМ МЕСТО (КРИТИЧНО!)
            location_equipment = workout_info.get('location_equipment', '').lower()
            is_home = any(word in location_equipment for word in ['дом', 'home', 'uy'])
            is_gym = any(word in location_equipment for word in ['зал', 'gym', 'sport zal', 'тренажерн'])
            is_outdoor = any(word in location_equipment for word in ['улиц', 'outdoor', 'street', 'парк', 'park', 'ko\'cha'])

            if is_home or is_outdoor:
                location = 'home'
                equipment_type = 'bodyweight'  # Только вес тела!
            elif is_gym:
                location = 'gym'
                equipment_type = 'full'  # Все оборудование
            else:
                location = 'home'  # По умолчанию - дома без инвентаря
                equipment_type = 'bodyweight'

            # 3. ОПРЕДЕЛЯЕМ ТИП ТРЕНИРОВКИ
            muscle_group = workout_info.get("muscle_group", "full_body")
            workout_type_map = {
                "chest": "strength",
                "back": "strength",
                "legs": "strength",
                "arms": "strength",
                "shoulders": "strength",
                "full_body": "full_body",
                "cardio": "cardio",
                "flexibility": "flexibility"
            }
            workout_type = workout_type_map.get(muscle_group, "strength")

            # 4. ТОЧНЫЙ РАСЧЕТ ВРЕМЕНИ И УПРАЖНЕНИЙ
            duration_str = workout_info.get('duration', '45-60')
            try:
                duration = int(''.join(filter(str.isdigit, duration_str.split('-')[0])))
            except:
                duration = 45

            # УМНЫЙ РАСЧЕТ количества упражнений:
            # 30 мин = 3, 45 мин = 4, 60 мин = 5
            level = profile.get('level', 'intermediate')
            energy = workout_info.get('energy_level', 'medium')

            if duration <= 30:
                base_exercises = 3
            elif duration <= 45:
                base_exercises = 4
            elif duration <= 60:
                base_exercises = 5
            else:
                base_exercises = 6

            # Корректировка по энергии (только увеличиваем при высокой)
            if energy == 'high':
                base_exercises = min(7, base_exercises + 1)
            # При низкой энергии оставляем базовое количество

            # 5. ГЕНЕРИРУЕМ ПЛАН через улучшенный загрузчик
            workout_plan = workouts_loader.get_enhanced_workout_plan(
                goal=goal,
                location=location,
                workout_type=workout_type,
                duration_minutes=duration,
                level=level,
                muscle_group=muscle_group,
                equipment_type=equipment_type,
                energy_level=energy,
                exercise_count=base_exercises
            )

            # 6. СОЗДАЕМ ДЕТАЛЬНЫЙ ТЕКСТ ПЛАНА
            exercises = workout_plan['exercises']

            # ПЛАНКА ВСЕГДА В КОНЦЕ - сортируем упражнения
            if exercises:
                plank_exercises = []
                other_exercises = []
                for ex in exercises:
                    name = ex.get('Название упражнения', '').lower()
                    if 'планка' in name or 'plank' in name:
                        plank_exercises.append(ex)
                    else:
                        other_exercises.append(ex)
                exercises = other_exercises + plank_exercises

            recommendations = workout_plan['recommendations']
            estimated_calories = workout_plan['estimated_calories']
            warmup = workout_plan.get('warmup', [])
            cooldown = workout_plan.get('cooldown', [])

            # ПЕРЕВОДЫ
            titles = {
                'ru': '💪 ПЕРСОНАЛЬНЫЙ ПЛАН ТРЕНИРОВКИ',
                'en': '💪 PERSONAL WORKOUT PLAN',
                'uz': '💪 SHAXSIY MASHG\'ULOT REJASI'
            }

            # Определяем название места для вывода
            if is_outdoor:
                location_display = 'outdoor'
            elif is_home:
                location_display = 'home'
            elif is_gym:
                location_display = 'gym'
            else:
                location_display = 'home'

            location_names = {
                'ru': {'gym': '🏋️ Тренажерный зал', 'home': '🏠 Дома (без инвентаря)', 'outdoor': '🌳 На улице'},
                'en': {'gym': '🏋️ Gym', 'home': '🏠 Home (bodyweight)', 'outdoor': '🌳 Outdoor'},
                'uz': {'gym': '🏋️ Sport zali', 'home': '🏠 Uyda (inventarsiz)', 'outdoor': '🌳 Ko\'chada'}
            }

            energy_names = {
                'ru': {'high': 'Высокая', 'medium': 'Средняя', 'low': 'Низкая', 'recovery': 'Восстановление'},
                'en': {'high': 'High', 'medium': 'Medium', 'low': 'Low', 'recovery': 'Recovery'},
                'uz': {'high': 'Yuqori', 'medium': 'O\'rta', 'low': 'Past', 'recovery': 'Tiklanish'}
            }

            level_names = {
                'ru': {'beginner': 'Новичок', 'intermediate': 'Средний', 'advanced': 'Продвинутый'},
                'en': {'beginner': 'Beginner', 'intermediate': 'Intermediate', 'advanced': 'Advanced'},
                'uz': {'beginner': 'Boshlang\'ich', 'intermediate': 'O\'rta', 'advanced': 'Murakkab'}
            }

            # ЗАГОЛОВОК (без лишних рамок)
            plan_text = f"{titles.get(lang, titles['ru'])}\n\n"

            # ПАРАМЕТРЫ ТРЕНИРОВКИ (компактно)
            plan_text += f"📍 {location_names.get(lang, location_names['ru'])[location_display]}\n"
            plan_text += f"⏱ {duration} " + ("мин" if lang == 'ru' else "min" if lang == 'en' else "daq") + f" | 🔥 ~{estimated_calories} " + ("ккал" if lang == 'ru' else "kcal" if lang == 'en' else "kkal") + "\n"
            plan_text += f"💪 {level_names.get(lang, level_names['ru'])[level]} | ⚡ {energy_names.get(lang, energy_names['ru'])[energy]}\n\n"

            # РАЗМИНКА (5-7 минут)
            if warmup:
                plan_text += "🔥 " + ("РАЗМИНКА" if lang == 'ru' else "WARM-UP" if lang == 'en' else "ISITISH") + "\n"
                for i, w in enumerate(warmup, 1):
                    plan_text += f"  {i}. {w['name']} - {w['duration']}\n"
                plan_text += "\n"

            # ОСНОВНАЯ ЧАСТЬ
            plan_text += "💪 " + ("УПРАЖНЕНИЯ" if lang == 'ru' else "EXERCISES" if lang == 'en' else "MASHQLAR") + f" ({len(exercises)})\n\n"

            for i, exercise in enumerate(exercises, 1):
                name = exercise.get('Название упражнения', 'Упражнение')

                plan_text += f"▸ {i}. {name}\n"

                # Работающие мышцы
                muscles = exercise.get('Мышечные группы', exercise.get('Работающие мышцы', ''))
                if muscles and muscles != 'Комплексное упражнение':
                    plan_text += f"  💪 {muscles}\n"

                # ДЕТАЛЬНАЯ ТЕХНИКА (полностью)
                technique = exercise.get('Техника выполнения', '')
                if technique:
                    plan_text += f"  📖 Техника:\n"
                    if isinstance(technique, list):
                        for step in technique[:4]:  # Максимум 4 шага
                            plan_text += f"     • {step}\n"
                    else:
                        plan_text += f"     {technique}\n"

                # ВАЖНЫЕ МОМЕНТЫ
                important = exercise.get('Важные моменты', [])
                if important:
                    plan_text += f"  ⚠️ Важно:\n"
                    if isinstance(important, list):
                        for point in important[:3]:  # Максимум 3 пункта
                            plan_text += f"     • {point}\n"
                    else:
                        plan_text += f"     • {important}\n"

                # РЕКОМЕНДАЦИИ
                if 'Рекомендации' in exercise:
                    ex_rec = exercise['Рекомендации']
                    sets = ex_rec.get('Подходы', '3')
                    reps = ex_rec.get('Повторения', '12')
                    rest = ex_rec.get('Отдых между подходами', '60 сек')
                    plan_text += f"  📊 {sets} × {reps} | ⏱ {rest}\n"

                plan_text += "\n"

            # ЗАМИНКА
            if cooldown:
                plan_text += "🧘 " + ("ЗАМИНКА" if lang == 'ru' else "COOL-DOWN" if lang == 'en' else "CHO'ZISH") + "\n"
                for i, c in enumerate(cooldown, 1):
                    plan_text += f"  {i}. {c['name']} - {c['duration']}\n"
                plan_text += "\n"

            # ФИНАЛЬНАЯ МОТИВАЦИЯ (коротко)
            motivation = {
                'ru': "🏆 Удачной тренировки!",
                'en': "🏆 Good workout!",
                'uz': "🏆 Omadli mashg'ulot!"
            }
            plan_text += motivation.get(lang, motivation['ru'])

            logger.info(f"✅ Детальный план создан ({len(exercises)} упражнений, {duration} мин)")
            return plan_text

        except Exception as e:
            logger.error(f"❌ Ошибка генерации: {e}")
            import traceback
            traceback.print_exc()

            # Fallback
            fallback = {
                'ru': "💪 БАЗОВАЯ ТРЕНИРОВКА\n\n1. Разминка 5-10 минут\n2. Основные упражнения 30-40 минут\n3. Заминка 5-10 минут",
                'en': "💪 BASIC WORKOUT\n\n1. Warm-up 5-10 minutes\n2. Main exercises 30-40 minutes\n3. Cool-down 5-10 minutes",
                'uz': "💪 ASOSIY MASHG'ULOT\n\n1. Isitish 5-10 daqiqa\n2. Asosiy mashqlar 30-40 daqiqa\n3. Cho'zish 5-10 daqiqa"
            }
            return fallback.get(lang, fallback['ru'])

    @staticmethod
    def generate_tip(user_id: int = None):
        """Генерирует полезный совет"""

        # Определяем язык пользователя
        lang = "ru"
        if user_id:
            user = db.get_user(user_id)
            if user:
                lang = user.get("language", "ru")
                set_log_lang(lang)

        # База советов
        tips_database = {
            'ru': [
                "💡 Пейте 2-3 литра воды в день для поддержания метаболизма и энергии.",
                "💡 Спите 7-9 часов для эффективного восстановления мышц и сжигания жира.",
                "💡 Увеличивайте вес постепенно - по 2.5-5кг в неделю для безопасного прогресса.",
                "💡 Ешьте белок в течение 2 часов после тренировки для роста мышц.",
                "💡 Делайте разминку 5-10 минут перед тренировкой для предотвращения травм.",
                "💡 Ведите дневник тренировок для отслеживания прогресса.",
                "💡 Сложные углеводы (овсянка, гречка) дают энергию на весь день.",
                "💡 Здоровые жиры (орехи, рыба) необходимы для гормонального баланса.",
                "💡 Тренируйте каждую группу мышц 2-3 раза в неделю для роста.",
                "💡 Отдыхайте 1-2 дня в неделю для полного восстановления."
            ],
            'en': [
                "💡 Drink 2-3 liters of water daily to maintain metabolism and energy.",
                "💡 Sleep 7-9 hours for effective muscle recovery and fat burning.",
                "💡 Increase weight gradually - 2.5-5kg per week for safe progress.",
                "💡 Eat protein within 2 hours after workout for muscle growth.",
                "💡 Warm up 5-10 minutes before training to prevent injuries.",
                "💡 Keep a workout journal to track progress.",
                "💡 Complex carbs (oatmeal, buckwheat) provide all-day energy.",
                "💡 Healthy fats (nuts, fish) are essential for hormonal balance.",
                "💡 Train each muscle group 2-3 times per week for growth.",
                "💡 Rest 1-2 days per week for full recovery."
            ],
            'uz': [
                "💡 Metabolizm va energiyani saqlash uchun kuniga 2-3 litr suv iching.",
                "💡 Mushaklar tiklanishi va yog' yoqilishi uchun 7-9 soat uxlang.",
                "💡 Xavfsiz taraqqiyot uchun vaznni asta-sekin - haftasiga 2.5-5kg oshiring.",
                "💡 Mushaklar o'sishi uchun mashg'ulotdan keyin 2 soat ichida protein iste'mol qiling.",
                "💡 Jarohatlarning oldini olish uchun mashg'ulotdan oldin 5-10 daqiqa isinib oling.",
                "💡 Taraqqiyotni kuzatish uchun mashg'ulot kundaligini yuritib boring.",
                "💡 Murakkab uglevodlar (jo'xori, grechka) kun bo'yi energiya beradi.",
                "💡 Foydali yog'lar (yong'oq, baliq) gormonal muvozanat uchun zarur.",
                "💡 O'sish uchun har bir mushak guruhini haftada 2-3 marta mashq qiling.",
                "💡 To'liq tiklanish uchun haftada 1-2 kun dam oling."
            ]
        }

        import random
        tips = tips_database.get(lang, tips_database['ru'])
        return random.choice(tips)

async def quick_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрая команда /p для тестирования (только для админов)"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru") if user else "ru"

    if user_id not in ADMIN_IDS:
        await update.message.reply_text(t("admin_only_command", lang))
        return

    if not user or not user.get("profile"):
        await update.message.reply_text(t("create_profile_first", lang))
        return
    
    profile = user["profile"]
    
    # Рандомные данные для плана питания
    nutrition_prefs = {
        "available_products": random.choice([
            "курица, рис, овощи, яйца, творог",
            "говядина, гречка, овощи, рыба, молоко",
            "индейка, макароны, овощи, сыр, йогурт"
        ]),
        "exclude": random.choice(["Нет", "молочное", "глютен"]),
        "allergies": "Нет",
        "favorites": random.choice(["паста", "стейки", "салаты"]),
        "meals_structure": random.choice([
            "завтрак, обед, ужин",
            "завтрак, перекус, обед, перекус, ужин",
            "4-5 равных приёмов"
        ]),
        "meals_count": random.choice(["3 основных приема", "3 основных + 2 перекуса", "4-5 равномерных приемов"]),
        "cooking_time": random.choice([
            "Полноценная готовка (плита, духовка)",
            "Минимальная готовка (микроволновка, варка)",
            "Только готовые продукты (без готовки)"
        ])
    }
    
    # Рандомные данные для тренировки
    workout_prefs = {
        "location_equipment": random.choice([
            "Зал со всем оборудованием",
            "Дома с гантелями",
            "Дома без оборудования"
        ]),
        "duration": random.choice(["30 минут", "45-60 минут", "1.5 часа"]),
        "energy_level": random.choice(["high", "medium", "low", "recovery"]),
        "muscle_group": random.choice(["chest", "back", "legs", "full_body", "cardio"])
    }
    
    await update.message.reply_text(t("generating_nutrition_plan", lang))

    try:
        # План питания
        nutrition_plan = AIGenerator.generate_nutrition_plan(profile, nutrition_prefs)
        calories = calculate_calories(profile)

        # Парсинг калорий из плана
        parsed_cals = parse_calories_from_text(nutrition_plan)

        await update.message.reply_text(f"{t('nutrition_plan_title', lang)}\n\n{nutrition_plan[:1000]}...\n\n✅ {t('parsing_calories', lang)}: {parsed_cals} {t('kcal', lang)}")

        await update.message.reply_text(t("generating_workout_plan", lang))

        # План тренировки
        workout_plan = AIGenerator.generate_workout_plan(profile, workout_prefs)

        # Парсинг сожженных калорий
        workout_cals = parse_workout_calories(workout_plan)

        await update.message.reply_text(f"{t('workout_plan_title', lang)}\n\n{workout_plan[:1000]}...\n\n🔥 {t('calories_burned', lang)}: {workout_cals} {t('kcal', lang)}")

        # Сохраняем результаты
        save_daily_results(user_id, parsed_cals, workout_cals)

    except Exception as e:
        logger.error(f"Quick test error: {e}")
        await update.message.reply_text(t("error_occurred", lang).format(error=str(e)))

def get_main_menu(lang="ru"):
    # Текст для кнопки статистики
    stats_text = {
        'ru': '📊 Статистика тренировок',
        'en': '📊 Workout Statistics',
        'uz': '📊 Mashg\'ulot statistikasi'
    }

    # Текст для кнопки чата с нейросетью
    chat_text = {
        'ru': '🤖 Говорить с нейросетью',
        'en': '🤖 Chat with AI',
        'uz': '🤖 Sun\'iy intellekt bilan suhbat'
    }

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t('profile', lang), callback_data="profile"),
         InlineKeyboardButton(t('results', lang), callback_data="results")],
        [InlineKeyboardButton(t('daily_program', lang), callback_data="daily_program")],
        [InlineKeyboardButton(stats_text.get(lang, stats_text['ru']), callback_data="workout_stats")],
        [InlineKeyboardButton(chat_text.get(lang, chat_text['ru']), callback_data="ai_chat"),
         InlineKeyboardButton(t('water_tracking', lang), callback_data="water_tracking")],
        [InlineKeyboardButton(t('achievements', lang), callback_data="achievements")],
        [InlineKeyboardButton(t('referrals', lang), callback_data="referrals")],
        [InlineKeyboardButton(t('instructions', lang), callback_data="instructions"),
         InlineKeyboardButton(t('contacts', lang), callback_data="contacts")]
    ])

def get_admin_menu(lang="ru"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t('view_stats', lang), callback_data="admin_stats")],
        [InlineKeyboardButton(t('broadcast', lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(t('user_management', lang), callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton(t('admin_knowledge_base', lang), callback_data="admin_knowledge")],
        [InlineKeyboardButton(t('admin_ai_training', lang), callback_data="admin_ai_training")],
        [InlineKeyboardButton(t('back', lang), callback_data="main_menu")]
    ])

def get_admin_settings_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("settings_target_cals", "ru"), callback_data="edit_target_cals")],
        [InlineKeyboardButton(t("settings_activity", "ru"), callback_data="edit_activity")],
        [InlineKeyboardButton(t("settings_prices", "ru"), callback_data="edit_prices")],
        [InlineKeyboardButton(t("settings_prompt_nutrition", "ru"), callback_data="edit_prompt_nutrition")],
        [InlineKeyboardButton(t("settings_prompt_workout", "ru"), callback_data="edit_prompt_workout")],
        [InlineKeyboardButton(t("settings_prompt_tips", "ru"), callback_data="edit_prompt_tips")],
        [InlineKeyboardButton(t("settings_save", "ru"), callback_data="admin_save_settings")],
        [InlineKeyboardButton(t("btn_back_menu", "ru"), callback_data="admin_menu")]
    ])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    user = db.get_user(user_id)
    
    # Обработка реферальной ссылки
    if context.args:
        ref_code = context.args[0]
        if ref_code.startswith("REF"):
            referrer_id = int(ref_code[3:])
            if referrer_id != user_id and db.get_user(referrer_id):
                if not user:
                    user = db.create_user(user_id, username)
                db.update_user(user_id, {"referred_by": referrer_id})
    
    # Создаем пользователя, если его нет
    if not user:
        user = db.create_user(user_id, username)
    
    # ВСЕГДА спрашиваем язык первым делом, если не выбран
    if not user.get("language"):
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")]
        ]
        await update.message.reply_text(
            t("choose_language", "ru"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LANGUAGE_SELECT
    
    # Проверяем, что профиль ПОЛНОСТЬЮ заполнен
    profile_complete = (
        user and 
        user.get("profile") and 
        user["profile"].get("name") and
        user["profile"].get("age") and
        user["profile"].get("gender") and
        user["profile"].get("height") and
        user["profile"].get("weight") and
        user["profile"].get("goal") and
        user["profile"].get("level")
    )
    
    # Если профиль полностью заполнен - показываем меню
    if profile_complete:
        lang = user.get("language", "ru")
        await update.message.reply_text(t("welcome_back", lang), reply_markup=get_main_menu(lang))
        return ConversationHandler.END
    
    # ВСЕГДА запускаем заполнение профиля, если он не полный
    lang = user.get("language", "ru")

    # Отправляем красивый приветственный баннер
    welcome_banner = visual_banners.welcome_banner()
    await update.message.reply_text(welcome_banner)

    await update.message.reply_text(t("welcome", lang))
    await update.message.reply_text(t("ask_name", lang))
    return PROFILE_NAME

async def language_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_map = {"lang_ru": "ru", "lang_en": "en", "lang_uz": "uz"}
    selected_lang = lang_map.get(query.data, "ru")
    
    user_id = query.from_user.id
    db.update_user(user_id, {"language": selected_lang})
    context.user_data["language"] = selected_lang
    
    # Устанавливаем язык для логирования
    set_log_lang(selected_lang)
    logger.info(f"User {user_id} selected language: {selected_lang}")
    
    await query.edit_message_text(t("welcome", selected_lang))
    await query.message.reply_text(t("ask_name", selected_lang))
    return PROFILE_NAME

async def profile_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")
    
    context.user_data["name"] = update.message.text
    await update.message.reply_text(t("ask_age", lang))
    return PROFILE_AGE

async def profile_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")
    
    try:
        age = int(update.message.text)
        if age < 16 or age > 100:
            await update.message.reply_text(t("age_error", lang))
            return PROFILE_AGE
        context.user_data["age"] = age
        
        keyboard = [[InlineKeyboardButton(t("male", lang), callback_data="gender_male")],
                   [InlineKeyboardButton(t("female", lang), callback_data="gender_female")]]
        await update.message.reply_text(t("ask_gender", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        return PROFILE_GENDER
    except ValueError:
        await update.message.reply_text(t("enter_number_example", lang).format(example="25"))
        return PROFILE_AGE

async def profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")
    
    context.user_data["gender"] = "male" if query.data == "gender_male" else "female"
    await query.edit_message_text(t("ask_height", lang))
    return PROFILE_HEIGHT

async def profile_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")

    try:
        height = int(update.message.text)
        if height < 120 or height > 250:
            await update.message.reply_text(t("height_error", lang))
            return PROFILE_HEIGHT
        context.user_data["height"] = height
        await update.message.reply_text(t("ask_weight", lang))
        return PROFILE_WEIGHT
    except ValueError:
        await update.message.reply_text(f"{t('number_error', lang)} (175)")
        return PROFILE_HEIGHT

async def profile_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")

    try:
        weight = float(update.message.text)
        if weight < 35 or weight > 250:
            await update.message.reply_text(t("weight_error", lang))
            return PROFILE_WEIGHT
        context.user_data["weight"] = weight

        keyboard = [[InlineKeyboardButton(t("goal_lose", lang), callback_data="goal_lose_weight")],
                   [InlineKeyboardButton(t("goal_gain", lang), callback_data="goal_gain_muscle")],
                   [InlineKeyboardButton(t("goal_maintain", lang), callback_data="goal_maintain")]]
        await update.message.reply_text(t("ask_goal", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        return PROFILE_GOAL
    except ValueError:
        await update.message.reply_text(f"{t('number_error', lang)} (70)")
        return PROFILE_WEIGHT

async def profile_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")

    goal_map = {"goal_lose_weight": "lose_weight", "goal_gain_muscle": "gain_muscle", "goal_maintain": "maintain"}
    context.user_data["goal"] = goal_map[query.data]

    keyboard = [[InlineKeyboardButton(t("level_beginner", lang), callback_data="level_beginner")],
               [InlineKeyboardButton(t("level_intermediate", lang), callback_data="level_intermediate")],
               [InlineKeyboardButton(t("level_advanced", lang), callback_data="level_advanced")]]
    await query.edit_message_text(t("ask_level", lang), reply_markup=InlineKeyboardMarkup(keyboard))
    return PROFILE_LEVEL

async def profile_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")

    level_map = {"level_beginner": "beginner", "level_intermediate": "intermediate", "level_advanced": "advanced"}
    context.user_data["level"] = level_map[query.data]
    await query.edit_message_text(t("ask_limitations", lang))
    return PROFILE_LIMITATIONS

async def profile_limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get("language", "ru")

    limitations = update.message.text if update.message.text != "-" else t("none_text", lang)
    context.user_data["limitations"] = limitations

    profile_data = {k: context.user_data.get(k) for k in ["name", "age", "gender", "height", "weight", "goal", "level", "limitations"]}

    calories = calculate_calories(profile_data)

    db.update_user(user_id, {"profile": profile_data})

    goal_text = {
        "lose_weight": t("goal_lose_weight", lang),
        "gain_muscle": t("goal_gain_muscle", lang),
        "maintain": t("goal_maintain_form", lang)
    }

    completion_text = f"""{t("profile_created", lang)}

{t("profile_calculations", lang)}

🔥 {t("bmr", lang)}: {calories['bmr']} {t("kcal_day", lang)}
⚡️ {t("tdee", lang)}: {calories['tdee']} {t("kcal_day", lang)}
🎯 {t("target_calories", lang)}: {calories['daily_calories']} {t("kcal_day", lang)}

⚖️ {t("macro_balance", lang)}:
- {t("proteins", lang)}: {calories['protein_g']} г
- {t("fats", lang)}: {calories['fats_g']} г
- {t("carbs", lang)}: {calories['carbs_g']} г

📈 {t("forecast", lang)}:
{t("goal", lang)}: {goal_text.get(profile_data['goal'], '')}
- {t("weekly_change", lang)}: {abs(calories['weekly_change'])} {t("kg", lang)}
- {t("ideal_weight", lang)}: {calories['ideal_weight_range']}

{t("trial_period", lang)}

{t("ready_start", lang)}"""

    await update.message.reply_text(completion_text, reply_markup=get_main_menu(lang))
    context.user_data.clear()
    return ConversationHandler.END

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        await update.message.reply_text(t("admin_no_access", lang))
        return

    user = db.get_user(user_id)
    lang = user.get("language", "ru") if user else "ru"

    stats = db.get_stats()
    admin_text = f"""{t("admin_panel", lang)}

{t("statistics", lang)}
{t("total_users", lang)} {stats['total_users']}
{t("active_subscriptions", lang)} {stats['active_subscriptions']}

{t("choose_action", lang)}"""

    await update.message.reply_text(admin_text, reply_markup=get_admin_menu(lang))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "main_menu":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        await query.edit_message_text(t("main_menu", lang), reply_markup=get_main_menu(lang))
    
    elif data == "profile":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        if not user or not user.get("profile"):
            await query.edit_message_text(t("profile_not_filled", lang))
            return

        profile = user["profile"]
        gender_text = t("male", lang) if profile.get("gender") == "male" else t("female", lang)
        goal_text = {
            "lose_weight": t("goal_lose_weight", lang),
            "gain_muscle": t("goal_gain_muscle", lang),
            "maintain": t("goal_maintain_form", lang)
        }
        level_text = {
            "beginner": t("level_beginner_text", lang),
            "intermediate": t("level_intermediate_text", lang),
            "advanced": t("level_advanced_text", lang)
        }

        profile_text = f"""{t("your_profile", lang)}

{t("personal_data", lang)}:
- {t("name", lang)}: {profile.get('name')}
- {t("age", lang)}: {profile.get('age')} {t("years", lang)}
- {t("gender", lang)}: {gender_text}
- {t("height", lang)}: {profile.get('height')} {t("cm", lang)}
- {t("weight", lang)}: {profile.get('weight')} {t("kg", lang)}

{t("fitness_goals", lang)}:
- {t("goal", lang)}: {goal_text.get(profile.get('goal'))}
- {t("level", lang)}: {level_text.get(profile.get('level'))}
- {t("limitations", lang)}: {profile.get('limitations')}

{t("subscription_status", lang)}: {t("active", lang) if db.has_active_subscription(user_id) else t("inactive", lang)}"""

        keyboard = [[InlineKeyboardButton(t("edit_profile", lang), callback_data="edit_profile")],
                   [InlineKeyboardButton(t("return_menu", lang), callback_data="main_menu")]]
        await query.edit_message_text(profile_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "edit_profile":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        
        keyboard = [
            [InlineKeyboardButton(t('name', lang), callback_data="edit_prof_name")],
            [InlineKeyboardButton(t('age', lang), callback_data="edit_prof_age")],
            [InlineKeyboardButton(t('gender', lang), callback_data="edit_prof_gender")],
            [InlineKeyboardButton(t('height', lang), callback_data="edit_prof_height")],
            [InlineKeyboardButton(t('weight', lang), callback_data="edit_prof_weight")],
            [InlineKeyboardButton(t('goal', lang), callback_data="edit_prof_goal")],
            [InlineKeyboardButton(t('level', lang), callback_data="edit_prof_level")],
            [InlineKeyboardButton(t('limitations', lang), callback_data="edit_prof_limitations")],
            [InlineKeyboardButton(t('language', lang), callback_data="edit_prof_language")],
            [InlineKeyboardButton(t('back', lang), callback_data="profile")]
        ]
        
        edit_text = {
            "ru": "Выберите, что хотите изменить:",
            "en": "Select what you want to change:",
            "uz": "O'zgartirmoqchi bo'lgan narsani tanlang:"
        }
        await query.edit_message_text(edit_text.get(lang, edit_text["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("edit_prof_"):
        edit_field = data.replace("edit_prof_", "")
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        
        if edit_field == "name":
            prompts = {
                "ru": "📝 Введите новое имя:",
                "en": "📝 Enter new name:",
                "uz": "📝 Yangi ismni kiriting:"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]))
            context.user_data["editing_profile"] = "name"
        elif edit_field == "age":
            prompts = {
                "ru": "🎂 Введите новый возраст (от 16 до 100):",
                "en": "🎂 Enter new age (16 to 100):",
                "uz": "🎂 Yangi yoshni kiriting (16 dan 100 gacha):"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]))
            context.user_data["editing_profile"] = "age"
        elif edit_field == "gender":
            keyboard = [[InlineKeyboardButton(t("male", lang), callback_data="set_prof_gender_male")],
                       [InlineKeyboardButton(t("female", lang), callback_data="set_prof_gender_female")]]
            prompts = {
                "ru": "⚧ Выберите пол:",
                "en": "⚧ Select gender:",
                "uz": "⚧ Jinsni tanlang:"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))
        elif edit_field == "height":
            prompts = {
                "ru": "📏 Введите новый рост в см (от 120 до 250):",
                "en": "📏 Enter new height in cm (120 to 250):",
                "uz": "📏 Yangi bo'yni sm da kiriting (120 dan 250 gacha):"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]))
            context.user_data["editing_profile"] = "height"
        elif edit_field == "weight":
            prompts = {
                "ru": "⚖️ Введите новый вес в кг (от 35 до 250):",
                "en": "⚖️ Enter new weight in kg (35 to 250):",
                "uz": "⚖️ Yangi vaznni kg da kiriting (35 dan 250 gacha):"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]))
            context.user_data["editing_profile"] = "weight"
        elif edit_field == "goal":
            keyboard = [[InlineKeyboardButton(t("goal_lose", lang), callback_data="set_prof_goal_lose")],
                       [InlineKeyboardButton(t("goal_gain", lang), callback_data="set_prof_goal_gain")],
                       [InlineKeyboardButton(t("goal_maintain", lang), callback_data="set_prof_goal_maintain")]]
            prompts = {
                "ru": "🎯 Выберите цель:",
                "en": "🎯 Select goal:",
                "uz": "🎯 Maqsadni tanlang:"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))
        elif edit_field == "level":
            keyboard = [[InlineKeyboardButton(t("level_beginner", lang), callback_data="set_prof_level_beginner")],
                       [InlineKeyboardButton(t("level_intermediate", lang), callback_data="set_prof_level_intermediate")],
                       [InlineKeyboardButton(t("level_advanced", lang), callback_data="set_prof_level_advanced")]]
            prompts = {
                "ru": "💪 Выберите уровень:",
                "en": "💪 Select level:",
                "uz": "💪 Darajani tanlang:"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))
        elif edit_field == "limitations":
            prompts = {
                "ru": "🚫 Введите ограничения (или '-' если нет):",
                "en": "🚫 Enter limitations (or '-' if none):",
                "uz": "🚫 Cheklovlarni kiriting (yoki yo'q bo'lsa '-'):"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]))
            context.user_data["editing_profile"] = "limitations"
        elif edit_field == "language":
            keyboard = [
                [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
                [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")],
                [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang_uz")],
                [InlineKeyboardButton(t('back', lang), callback_data="edit_profile")]
            ]
            prompts = {
                "ru": "🌐 Выберите язык:",
                "en": "🌐 Select language:",
                "uz": "🌐 Tilni tanlang:"
            }
            await query.edit_message_text(prompts.get(lang, prompts["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("set_lang_"):
        new_lang = data.replace("set_lang_", "")
        user = db.get_user(user_id)
        db.update_user(user_id, {"language": new_lang})
        
        # Устанавливаем язык для логирования
        set_log_lang(new_lang)
        logger.info(f"User {user_id} changed language to: {new_lang}")
        
        success_messages = {
            "ru": "✅ Язык успешно изменен!",
            "en": "✅ Language successfully changed!",
            "uz": "✅ Til muvaffaqiyatli o'zgartirildi!"
        }
        
        await query.answer(success_messages.get(new_lang, success_messages["ru"]))
        await query.edit_message_text(
            success_messages.get(new_lang, success_messages["ru"]), 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t('back', new_lang), callback_data="profile")]])
        )
    
    elif data.startswith("set_prof_gender_"):
        gender = "male" if "male" in data else "female"
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        profile = user.get("profile", {})
        profile["gender"] = gender
        db.update_user(user_id, {"profile": profile})
        
        success_messages = {
            "ru": "✅ Пол обновлен!",
            "en": "✅ Gender updated!",
            "uz": "✅ Jins yangilandi!"
        }
        
        await query.answer(success_messages.get(lang, success_messages["ru"]))
        await query.edit_message_text(
            success_messages.get(lang, success_messages["ru"]),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t('back', lang), callback_data="profile")]])
        )
    
    elif data.startswith("set_prof_goal_"):
        goal_map = {"set_prof_goal_lose": "lose_weight", "set_prof_goal_gain": "gain_muscle", "set_prof_goal_maintain": "maintain"}
        goal = goal_map.get(data, "maintain")
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        profile = user.get("profile", {})
        profile["goal"] = goal
        db.update_user(user_id, {"profile": profile})

        success_messages = {
            "ru": "✅ Цель обновлена!",
            "en": "✅ Goal updated!",
            "uz": "✅ Maqsad yangilandi!"
        }

        await query.answer(success_messages.get(lang, success_messages["ru"]))
        await query.edit_message_text(
            success_messages.get(lang, success_messages["ru"]),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("back", lang), callback_data="profile")]])
        )
    
    elif data.startswith("set_prof_level_"):
        level_map = {"set_prof_level_beginner": "beginner", "set_prof_level_intermediate": "intermediate", "set_prof_level_advanced": "advanced"}
        level = level_map.get(data, "intermediate")
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        profile = user.get("profile", {})
        profile["level"] = level
        db.update_user(user_id, {"profile": profile})

        success_messages = {
            "ru": "✅ Уровень обновлен!",
            "en": "✅ Level updated!",
            "uz": "✅ Daraja yangilandi!"
        }

        await query.answer(success_messages.get(lang, success_messages["ru"]))
        await query.edit_message_text(
            success_messages.get(lang, success_messages["ru"]),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("back", lang), callback_data="profile")]])
        )
    
    elif data == "results":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        if not user or not user.get("profile"):
            await query.edit_message_text(t("profile_not_filled", lang))
            return

        calories = calculate_calories(user["profile"])
        goal_text = {
            "lose_weight": t("goal_lose_weight", lang),
            "gain_muscle": t("goal_gain_muscle", lang),
            "maintain": t("goal_maintain_form", lang)
        }
        
        # Прогресс по калориям и весу
        progress = calculate_weight_loss_progress(user_id)
        progress_text = ""
        if progress.get("weeks"):
            progress_text = f"\n\n📈 {t('progress_by_weeks', lang)}:\n"
            for week_data in progress["weeks"][-4:]:
                sign = "📉" if week_data["weight_change"] < 0 else "📈"
                progress_text += f"{sign} {week_data['week']}: {abs(week_data['weight_change'])} кг ({week_data['days']} дн)\n"

            total_sign = f"📉 {t('lost', lang)}" if progress["total_change"] < 0 else f"📈 {t('gained', lang)}"
            progress_text += f"\n🎯 {total_sign}: {abs(progress['total_change'])} кг"

        # Статистика калорий за последние 7 дней
        daily_results = user.get("daily_results", [])
        recent_results = daily_results[-7:] if len(daily_results) >= 7 else daily_results

        calories_stats = ""
        if recent_results:
            avg_nutrition = sum(r.get("nutrition_calories", 0) for r in recent_results) / len(recent_results)
            avg_workout = sum(r.get("workout_calories", 0) for r in recent_results) / len(recent_results)
            avg_net = avg_nutrition - avg_workout

            calories_stats = f"\n\n📊 {t('average_for_days', lang)} {len(recent_results)} {t('days_text', lang)}:\n"
            calories_stats += f"🍽 {t('nutrition_text', lang)}: {int(avg_nutrition)} {t('kcal_per_day', lang)}\n"
            calories_stats += f"🔥 {t('workouts_text', lang)}: {int(avg_workout)} {t('kcal_per_day', lang)}\n"
            calories_stats += f"📍 {t('net_text', lang)}: {int(avg_net)} {t('kcal_per_day', lang)}"

        results_text = f"""📊 {t('your_results', lang)}

🎯 {t('goal', lang)}: {goal_text.get(user["profile"].get('goal'))}
📏 {t('ideal_weight', lang)}: {calories['ideal_weight_range']}

🔥 {t('metabolism', lang)}:
- {t('basic_exchange', lang)} (BMR): {calories['bmr']} ккал
- {t('expense_with_activity', lang)} (TDEE): {calories['tdee']} ккал
- {t('target_calories_text', lang)}: {calories['daily_calories']} ккал

⚖️ {t('balance_bju', lang)}:
- {t('proteins_text', lang)}: {calories['protein_g']} г
- {t('fats_text', lang)}: {calories['fats_g']} г
- {t('carbs_text', lang)}: {calories['carbs_g']} г{calories_stats}{progress_text}"""
        
        keyboard = [[InlineKeyboardButton(t("btn_return_menu", lang), callback_data="main_menu")]]
        await query.edit_message_text(results_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "workout_complete":
        # Отметить тренировку как выполненную и собрать обратную связь
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        difficulty_texts = {
            'ru': {
                'title': "🎯 Как прошла тренировка?\n\nОцените сложность для корректировки следующего плана:",
                'hard': "😰 Слишком сложно",
                'perfect': "💪 В самый раз",
                'easy': "😊 Слишком легко"
            },
            'en': {
                'title': "🎯 How was the workout?\n\nRate the difficulty to adjust your next plan:",
                'hard': "😰 Too hard",
                'perfect': "💪 Just right",
                'easy': "😊 Too easy"
            },
            'uz': {
                'title': "🎯 Mashg'ulot qanday o'tdi?\n\nKeyingi rejani sozlash uchun qiyinlikni baholang:",
                'hard': "😰 Juda qiyin",
                'perfect': "💪 Aynan kerakli",
                'easy': "😊 Juda oson"
            }
        }

        texts = difficulty_texts.get(lang, difficulty_texts['ru'])
        keyboard = [
            [InlineKeyboardButton(texts['hard'], callback_data="difficulty_hard")],
            [InlineKeyboardButton(texts['perfect'], callback_data="difficulty_perfect")],
            [InlineKeyboardButton(texts['easy'], callback_data="difficulty_easy")]
        ]

        await query.edit_message_text(texts['title'], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("difficulty_"):
        # Сохранить обратную связь о тренировке
        difficulty = data.replace("difficulty_", "")
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        # Сохраняем фидбек
        workouts_loader.save_workout_feedback(user_id, difficulty)

        # Получаем персональный анализ
        analysis = workouts_loader.analyze_user_progress(user_id)

        thanks_texts = {
            'ru': "✅ Спасибо за обратную связь!\n\n",
            'en': "✅ Thanks for feedback!\n\n",
            'uz': "✅ Fikr-mulohazangiz uchun rahmat!\n\n"
        }

        progress_titles = {
            'ru': "📊 ВАШ ПРОГРЕСС:\n" + "─" * 40 + "\n",
            'en': "📊 YOUR PROGRESS:\n" + "─" * 40 + "\n",
            'uz': "📊 SIZNING TARAQQIYOTINGIZ:\n" + "─" * 40 + "\n"
        }

        response = thanks_texts.get(lang, thanks_texts['ru'])
        response += progress_titles.get(lang, progress_titles['ru'])

        if analysis:
            if lang == 'ru':
                response += f"🏋️ Всего тренировок: {analysis['total_workouts']}\n"
                response += f"📅 Дней подряд: {analysis['streak_days']}\n"
                response += f"💪 Лучшая серия: {analysis['best_streak']} дней\n\n"
            elif lang == 'en':
                response += f"🏋️ Total workouts: {analysis['total_workouts']}\n"
                response += f"📅 Days in a row: {analysis['streak_days']}\n"
                response += f"💪 Best streak: {analysis['best_streak']} days\n\n"
            else:
                response += f"🏋️ Jami mashg'ulotlar: {analysis['total_workouts']}\n"
                response += f"📅 Ketma-ket kunlar: {analysis['streak_days']}\n"
                response += f"💪 Eng yaxshi seriya: {analysis['best_streak']} kun\n\n"

            if analysis.get('strength_progress'):
                if lang == 'ru':
                    response += "📈 РОСТ СИЛЫ:\n"
                elif lang == 'en':
                    response += "📈 STRENGTH PROGRESS:\n"
                else:
                    response += "📈 KUCH O'SISHI:\n"

                for exercise, progress in list(analysis['strength_progress'].items())[:3]:
                    response += f"   • {exercise}: +{progress}%\n"
                response += "\n"

            if analysis.get('weak_points'):
                if lang == 'ru':
                    response += "⚠️ СЛАБЫЕ МЕСТА:\n"
                elif lang == 'en':
                    response += "⚠️ WEAK POINTS:\n"
                else:
                    response += "⚠️ ZAIF JOYLAR:\n"

                for weak in analysis['weak_points'][:2]:
                    response += f"   • {weak}\n"
                response += "\n"

            if analysis.get('recommendations'):
                if lang == 'ru':
                    response += "💡 РЕКОМЕНДАЦИИ ТРЕНЕРА:\n"
                elif lang == 'en':
                    response += "💡 TRAINER RECOMMENDATIONS:\n"
                else:
                    response += "💡 MURABBIY TAVSIЯЛARI:\n"

                for rec in analysis['recommendations'][:3]:
                    response += f"   ✓ {rec}\n"

        keyboard = [[InlineKeyboardButton(t("btn_return_menu", lang), callback_data="main_menu")]]
        await query.edit_message_text(response, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "workout_stats":
        # Показать детальную статистику тренировок
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        # Получаем полный анализ
        analysis = workouts_loader.get_detailed_analysis(user_id)

        if not analysis or analysis['total_workouts'] == 0:
            no_data_texts = {
                'ru': "📊 У вас пока нет тренировок.\nСоздайте первый план!",
                'en': "📊 You have no workouts yet.\nCreate your first plan!",
                'uz': "📊 Sizda hali mashg'ulotlar yo'q.\nBirinchi rejangizni yarating!"
            }
            await query.edit_message_text(
                no_data_texts.get(lang, no_data_texts['ru']),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t("btn_return_menu", lang), callback_data="main_menu")
                ]])
            )
            return

        stats_text = "📊 " + ("ДЕТАЛЬНАЯ СТАТИСТИКА" if lang == 'ru' else "DETAILED STATISTICS" if lang == 'en' else "BATAFSIL STATISTIKA") + "\n"
        stats_text += "═" * 40 + "\n\n"

        # Общая статистика
        if lang == 'ru':
            stats_text += f"🏋️ Всего тренировок: {analysis['total_workouts']}\n"
            stats_text += f"⏱ Общее время: {analysis['total_time']} минут\n"
            stats_text += f"🔥 Сожжено калорий: {analysis['total_calories']}\n"
            stats_text += f"📅 Текущая серия: {analysis['current_streak']} дней\n"
            stats_text += f"🏆 Лучшая серия: {analysis['best_streak']} дней\n\n"
        elif lang == 'en':
            stats_text += f"🏋️ Total workouts: {analysis['total_workouts']}\n"
            stats_text += f"⏱ Total time: {analysis['total_time']} minutes\n"
            stats_text += f"🔥 Calories burned: {analysis['total_calories']}\n"
            stats_text += f"📅 Current streak: {analysis['current_streak']} days\n"
            stats_text += f"🏆 Best streak: {analysis['best_streak']} days\n\n"
        else:
            stats_text += f"🏋️ Jami mashg'ulotlar: {analysis['total_workouts']}\n"
            stats_text += f"⏱ Umumiy vaqt: {analysis['total_time']} daqiqa\n"
            stats_text += f"🔥 Yoqilgan kaloriya: {analysis['total_calories']}\n"
            stats_text += f"📅 Joriy seriya: {analysis['current_streak']} kun\n"
            stats_text += f"🏆 Eng yaxshi seriya: {analysis['best_streak']} kun\n\n"

        # Прогресс по весам
        if analysis.get('weight_progress'):
            stats_text += "📈 " + ("ПРОГРЕСС ПО ВЕСАМ" if lang == 'ru' else "WEIGHT PROGRESS" if lang == 'en' else "VAZN BO'YICHA TARAQQIYOT") + ":\n"
            stats_text += "─" * 40 + "\n"
            for exercise, data_prog in list(analysis['weight_progress'].items())[:5]:
                start = data_prog['first']
                current = data_prog['last']
                increase = ((current - start) / start * 100) if start > 0 else 0
                stats_text += f"💪 {exercise}:\n"
                stats_text += f"   {start} " + ("кг" if lang == 'ru' else "kg") + f" → {current} " + ("кг" if lang == 'ru' else "kg") + f" (+{increase:.1f}%)\n"
            stats_text += "\n"

        # Любимые упражнения
        if analysis.get('favorite_exercises'):
            stats_text += "❤️ " + ("ЛЮБИМЫЕ УПРАЖНЕНИЯ" if lang == 'ru' else "FAVORITE EXERCISES" if lang == 'en' else "SEVIMLI MASHQLAR") + ":\n"
            stats_text += "─" * 40 + "\n"
            for i, (exercise, count) in enumerate(analysis['favorite_exercises'][:3], 1):
                stats_text += f"{i}. {exercise} ({count} " + ("раз" if lang == 'ru' else "times" if lang == 'en' else "marta") + ")\n"
            stats_text += "\n"

        # Слабые места
        if analysis.get('improvement_areas'):
            stats_text += "🎯 " + ("ЧТО УЛУЧШИТЬ" if lang == 'ru' else "WHAT TO IMPROVE" if lang == 'en' else "NIMANI YAXSHILASH") + ":\n"
            stats_text += "─" * 40 + "\n"
            for area in analysis['improvement_areas'][:3]:
                stats_text += f"⚡ {area}\n"

        keyboard = [
            [InlineKeyboardButton("📈 " + ("Прогноз результатов" if lang == 'ru' else "Results forecast" if lang == 'en' else "Natijalar prognozi"), callback_data="workout_forecast")],
            [InlineKeyboardButton(t("btn_return_menu", lang), callback_data="main_menu")]
        ]

        await query.edit_message_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "workout_forecast":
        # Прогноз будущих результатов
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        forecast = workouts_loader.forecast_progress(user_id)

        if not forecast:
            not_enough_texts = {
                'ru': "📊 Недостаточно данных для прогноза.\nВыполните минимум 5 тренировок!",
                'en': "📊 Not enough data for forecast.\nComplete at least 5 workouts!",
                'uz': "📊 Prognoz uchun ma'lumotlar yetarli emas.\nKamida 5 ta mashg'ulotni bajaring!"
            }
            await query.edit_message_text(
                not_enough_texts.get(lang, not_enough_texts['ru']),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(t("back", lang), callback_data="workout_stats")
                ]])
            )
            return

        forecast_text = "🔮 " + ("ПРОГНОЗ ВАШИХ РЕЗУЛЬТАТОВ" if lang == 'ru' else "YOUR RESULTS FORECAST" if lang == 'en' else "NATIJALARINGIZ PROGNOZI") + "\n"
        forecast_text += "═" * 40 + "\n\n"

        forecast_text += "📅 " + ("Через 1 месяц" if lang == 'ru' else "In 1 month" if lang == 'en' else "1 oydan keyin") + ":\n"
        for exercise, prediction in list(forecast['month'].items())[:3]:
            forecast_text += f"   💪 {exercise}: ~{prediction} " + ("кг" if lang == 'ru' else "kg") + "\n"

        forecast_text += "\n📅 " + ("Через 3 месяца" if lang == 'ru' else "In 3 months" if lang == 'en' else "3 oydan keyin") + ":\n"
        for exercise, prediction in list(forecast['quarter'].items())[:3]:
            forecast_text += f"   🏆 {exercise}: ~{prediction} " + ("кг" if lang == 'ru' else "kg") + "\n"

        forecast_text += "\n\n💡 " + ("КЛЮЧЕВЫЕ СОВЕТЫ" if lang == 'ru' else "KEY TIPS" if lang == 'en' else "ASOSIY MASLAHATLAR") + ":\n"
        forecast_text += "─" * 40 + "\n"
        for tip in forecast['tips']:
            forecast_text += f"✓ {tip}\n"

        keyboard = [[InlineKeyboardButton(t("back", lang), callback_data="workout_stats")]]
        await query.edit_message_text(forecast_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "daily_program":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        if not db.has_active_subscription(user_id):
            await query.edit_message_text(t("no_subscription", lang),
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("payment", lang), callback_data="payment")]]))
        else:
            keyboard = [[InlineKeyboardButton(t("btn_nutrition_plan", lang), callback_data="nutrition_plan")],
                       [InlineKeyboardButton(t("btn_workout_plan", lang), callback_data="workout_plan")],
                       [InlineKeyboardButton(t("btn_back_menu", lang), callback_data="main_menu")]]
            await query.edit_message_text(t("program_on_day", lang), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "nutrition_plan" or data == "regenerate_nutrition":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        if not db.has_active_subscription(user_id):
            await query.edit_message_text(t("need_subscription", lang))
            return

        # Очищаем старые данные если это regenerate
        if data == "regenerate_nutrition":
            if "nutrition_data" in context.user_data:
                del context.user_data["nutrition_data"]
            if "current_plan" in context.user_data:
                del context.user_data["current_plan"]

        await query.edit_message_text(t("nutrition_question_1", lang))
        context.user_data["nutrition_step"] = 1
        context.user_data["nutrition_data"] = {}
    
    elif data == "workout_plan" or data == "regenerate_workout":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        if not db.has_active_subscription(user_id):
            await query.edit_message_text(t("need_subscription", lang))
            return

        # Очищаем старые данные если это regenerate
        if data == "regenerate_workout":
            if "workout_data" in context.user_data:
                del context.user_data["workout_data"]
            if "current_plan" in context.user_data:
                del context.user_data["current_plan"]

        # Спрашиваем какую группу мышц тренировать
        keyboard = [
            [InlineKeyboardButton(t("chest", lang), callback_data="muscle_chest")],
            [InlineKeyboardButton(t("back_muscles", lang), callback_data="muscle_back")],
            [InlineKeyboardButton(t("legs", lang), callback_data="muscle_legs")],
            [InlineKeyboardButton(t("full_body", lang), callback_data="muscle_full_body")],
            [InlineKeyboardButton(t("cardio", lang), callback_data="muscle_cardio")]
        ]
        await query.edit_message_text(t("workout_selection", lang),
                                     reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["workout_step"] = 0
        context.user_data["workout_data"] = {}

    elif data.startswith("muscle_"):
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        muscle_group = data.replace("muscle_", "")
        context.user_data["workout_data"]["muscle_group"] = muscle_group

        await query.edit_message_text(t("workout_question_2", lang))
        context.user_data["workout_step"] = 1
    
    elif data == "daily_tip":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        now = datetime.now()

        # Админы получают безлимитные советы
        is_admin = user_id in ADMIN_IDS

        # Проверяем последний бесплатный совет
        last_tip = user.get("last_free_tip")
        can_get_free = False

        if last_tip:
            last_tip_time = datetime.fromisoformat(last_tip)
            time_diff = now - last_tip_time
            can_get_free = time_diff.total_seconds() >= 86400  # 24 часа
        else:
            can_get_free = True

        # Если можно получить бесплатный совет или пользователь админ
        if can_get_free or is_admin:
            loading_msg = await query.edit_message_text(t("generating_tip", lang))
            tip = AIGenerator.generate_tip(user_id=user_id)
            db.update_user(user_id, {"last_free_tip": now.isoformat()})

            # Считаем время до следующего бесплатного совета
            next_free_time = now + timedelta(hours=24)
            hours_left = 24

            keyboard = [
                [InlineKeyboardButton(t("tip_refresh_for_stars", lang), callback_data="buy_tip")],
                [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
            ]

            # Для админа показываем сообщение без ограничений
            if is_admin:
                tip_message = f"{t('tip_title', lang)}\n\n{tip}\n\n⭐ Безлимитные советы для админа!"
            else:
                tip_message = f"{t('tip_title', lang)}\n\n{tip}\n\n{t('tip_next_free', lang).format(hours=hours_left)}"

            await loading_msg.edit_text(tip_message, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            # Считаем оставшееся время
            last_tip_time = datetime.fromisoformat(last_tip)
            next_free_time = last_tip_time + timedelta(hours=24)
            time_left = next_free_time - now
            hours_left = int(time_left.total_seconds() / 3600)
            minutes_left = int((time_left.total_seconds() % 3600) / 60)

            keyboard = [
                [InlineKeyboardButton(t("tip_get_for_stars", lang), callback_data="buy_tip")],
                [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
            ]

            wait_message = f"{t('tip_wait_title', lang)}\n\n{t('tip_wait_message', lang).format(hours=hours_left, minutes=minutes_left)}"
            await query.edit_message_text(wait_message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "buy_tip":
        # Проверяем, есть ли у пользователя последний совет
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        has_previous_tip = user.get("last_free_tip") is not None

        title = t("tip_new_title", lang) if has_previous_tip else t("daily_tip", lang)
        description = t("tip_description", lang)
        payload = f"{user_id}:tip"
        prices = [LabeledPrice(label=title, amount=100)]

        await context.bot.send_invoice(
            chat_id=user_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="",
            currency="XTR",
            prices=prices
        )
        await query.answer(t("invoice_sent", lang))

    elif data == "water_tracking":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        # Инициализируем трекинг воды если нет
        if "water" not in user:
            user["water"] = {"consumed": 0, "goal": 2500, "last_reset": datetime.now().date().isoformat()}
            db.update_user(user_id, user)

        water_data = user.get("water", {})

        # Проверяем, нужно ли сбросить счетчик (новый день)
        last_reset = water_data.get("last_reset", datetime.now().date().isoformat())
        if last_reset != datetime.now().date().isoformat():
            water_data["consumed"] = 0
            water_data["last_reset"] = datetime.now().date().isoformat()
            user["water"] = water_data
            db.update_user(user_id, user)

        consumed = water_data.get("consumed", 0)

        message = f"{t('water_title', lang)}\n\n"
        message += f"💧 Выпито сегодня: {consumed} мл\n"
        message += f"📊 Это примерно {round(consumed / 1000, 1)} литров\n"

        keyboard = [
            [InlineKeyboardButton(t("water_add_250", lang), callback_data="water_add_250")],
            [InlineKeyboardButton(t("water_add_500", lang), callback_data="water_add_500")],
            [InlineKeyboardButton(t("water_add_1000", lang), callback_data="water_add_1000")],
            [InlineKeyboardButton(t("water_reset", lang), callback_data="water_reset")],
            [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
        ]

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("water_add_"):
        user = db.get_user(user_id)
        lang = user.get("language", "ru")
        amount = int(data.split("_")[-1])

        if "water" not in user:
            user["water"] = {"consumed": 0, "goal": 2500, "last_reset": datetime.now().date().isoformat()}

        water_data = user["water"]
        water_data["consumed"] = water_data.get("consumed", 0) + amount
        user["water"] = water_data
        db.update_user(user_id, user)

        consumed = water_data["consumed"]

        response_msg = f"✅ Добавлено {amount} мл"

        await query.answer(response_msg, show_alert=True)

        # Обновляем сообщение
        message = f"{t('water_title', lang)}\n\n"
        message += f"💧 Выпито сегодня: {consumed} мл\n"
        message += f"📊 Это примерно {round(consumed / 1000, 1)} литров\n"

        keyboard = [
            [InlineKeyboardButton(t("water_add_250", lang), callback_data="water_add_250")],
            [InlineKeyboardButton(t("water_add_500", lang), callback_data="water_add_500")],
            [InlineKeyboardButton(t("water_add_1000", lang), callback_data="water_add_1000")],
            [InlineKeyboardButton(t("water_reset", lang), callback_data="water_reset")],
            [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
        ]

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "water_reset":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        if "water" in user:
            user["water"]["consumed"] = 0
            user["water"]["last_reset"] = datetime.now().date().isoformat()
            db.update_user(user_id, user)

        await query.answer(t("water_reset_done", lang))

        # Обновляем сообщение
        message = f"{t('water_title', lang)}\n\n"
        message += f"💧 Выпито сегодня: 0 мл\n"
        message += f"📊 Это примерно 0.0 литров\n"

        keyboard = [
            [InlineKeyboardButton(t("water_add_250", lang), callback_data="water_add_250")],
            [InlineKeyboardButton(t("water_add_500", lang), callback_data="water_add_500")],
            [InlineKeyboardButton(t("water_add_1000", lang), callback_data="water_add_1000")],
            [InlineKeyboardButton(t("water_reset", lang), callback_data="water_reset")],
            [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
        ]

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "ai_chat":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        # Включаем режим чата
        user["chat_mode"] = True
        if "chat_history" not in user:
            user["chat_history"] = []
        db.update_user(user_id, user)

        chat_welcome = {
            "ru": "🤖 Режим разговора с нейросетью активирован!\n\nТеперь вы можете задавать мне любые вопросы о фитнесе, питании, здоровье или просто поговорить. Я здесь, чтобы помочь!\n\n💬 Напишите свой вопрос или сообщение...",
            "en": "🤖 AI Chat mode activated!\n\nNow you can ask me anything about fitness, nutrition, health or just chat. I'm here to help!\n\n💬 Type your question or message...",
            "uz": "🤖 Sun'iy intellekt bilan suhbat rejimi faollashtirildi!\n\nEndi siz menga fitness, ovqatlanish, salomatlik haqida yoki shunchaki suhbatlashish uchun har qanday savol berishingiz mumkin!\n\n💬 Savolingizni yoki xabaringizni yozing..."
        }

        keyboard = [[InlineKeyboardButton("🚪 " + t("back", lang), callback_data="end_ai_chat")]]
        await query.edit_message_text(chat_welcome.get(lang, chat_welcome["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "end_ai_chat":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        # Выключаем режим чата
        user["chat_mode"] = False
        db.update_user(user_id, user)

        goodbye_msg = {
            "ru": "👋 Разговор завершен. Возвращаю вас в главное меню.",
            "en": "👋 Chat ended. Returning to main menu.",
            "uz": "👋 Suhbat tugadi. Asosiy menyuga qaytaraman."
        }

        await query.edit_message_text(goodbye_msg.get(lang, goodbye_msg["ru"]), reply_markup=get_main_menu(lang))

    elif data == "profile_edit":

        keyboard = [
            [InlineKeyboardButton(t("water_add_250", lang), callback_data="water_add_250")],
            [InlineKeyboardButton(t("water_add_500", lang), callback_data="water_add_500")],
            [InlineKeyboardButton(t("water_add_1000", lang), callback_data="water_add_1000")],
            [InlineKeyboardButton(t("water_reset", lang), callback_data="water_reset")],
            [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
        ]

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "achievements":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        # Инициализируем достижения если нет
        if "achievements" not in user:
            user["achievements"] = []
            user["stats"] = {"workouts": 0, "nutrition_plans": 0, "days_streak": 0, "water_days": 0}
            db.update_user(user_id, user)

        achievements_list = user.get("achievements", [])
        stats = user.get("stats", {})

        message = f"{t('achievements_title', lang)}\n\n"

        if achievements_list:
            achievement_icons = {
                "first_workout": "💪",
                "week_streak": "🔥",
                "month_streak": "⭐",
                "water_goal": "💧",
                "10_workouts": "🏋️",
                "50_workouts": "💎"
            }

            for ach in achievements_list:
                icon = achievement_icons.get(ach, "🏆")
                ach_name = t(f"achievement_{ach}", lang)
                message += f"{icon} {ach_name}\n"

            message += f"\n{t('progress_stats', lang)}:\n"
            message += f"• {t('total_workouts', lang)}: {stats.get('workouts', 0)}\n"
            message += f"• {t('total_nutrition_plans', lang)}: {stats.get('nutrition_plans', 0)}\n"
            message += f"• {t('days_streak', lang)}: {stats.get('days_streak', 0)}\n"
            message += f"• {t('water_streak', lang)}: {stats.get('water_days', 0)}\n"
        else:
            message += t("no_achievements", lang)

        keyboard = [[InlineKeyboardButton(t("back", lang), callback_data="main_menu")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "payment":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        keyboard = [
            [InlineKeyboardButton("📅 1 день - 50⭐ / 100₽", callback_data="select_1_day")],
            [InlineKeyboardButton("📅 7 дней - 300⭐ / 600₽", callback_data="select_7_days")],
            [InlineKeyboardButton("📅 14 дней - 600⭐ / 1200₽", callback_data="select_14_days")],
            [InlineKeyboardButton(t("back", lang), callback_data="main_menu")]
        ]

        payment_info = f"""💎 PREMIUM ПОДПИСКА НА ФИТНЕС-БОТА

🏢 О нас:
Интеллектуальный AI-фитнес тренер с персональными программами питания и тренировок.

📋 Что вы получите:
✅ Персональные планы питания на каждый день
✅ Индивидуальные программы тренировок
✅ Расчет калорий и БЖУ под ваши цели
✅ Ежедневные советы от AI-тренера
✅ Трекинг прогресса и достижений
✅ База из 250+ рецептов
✅ Поддержка 24/7

🎯 Для чего:
• Похудение или набор массы
• Улучшение здоровья и формы
• Профессиональный подход к фитнесу
• Экономия на персональном тренере

💰 Выберите тариф:"""

        await query.edit_message_text(payment_info, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("select_"):
        # Показываем выбор способа оплаты для выбранного тарифа
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        subscription_key = data.replace("select_", "")
        if subscription_key not in SUBSCRIPTION_PRICES:
            await query.answer("❌ Неверный тип подписки")
            return

        sub_info = SUBSCRIPTION_PRICES[subscription_key]
        days_text = {
            "1_day": "1 день",
            "7_days": "7 дней",
            "14_days": "14 дней"
        }

        keyboard = [
            [InlineKeyboardButton(f"⭐ Telegram Stars ({sub_info['stars']} Stars)", callback_data=f"buy_{subscription_key}_stars")],
            [InlineKeyboardButton(f"💳 Банковская карта ({sub_info['rubles']} ₽)", callback_data=f"buy_{subscription_key}_rub")],
            [InlineKeyboardButton(t("back", lang), callback_data="payment")]
        ]

        message = f"""📦 ПОДПИСКА НА {days_text.get(subscription_key, subscription_key).upper()}

🏢 Провайдер: AI Fitness Coach Bot
📱 Канал поддержки: @ProSportRBKSupport

📋 Описание услуги:
Доступ к персональному AI-тренеру с полным функционалом на {days_text.get(subscription_key, subscription_key)}.

✨ Что входит:
• Персональные планы питания каждый день
• Программы тренировок под ваш уровень
• Точный расчет калорий и БЖУ
• Советы по питанию и спорту
• База из 250+ здоровых рецептов
• Отслеживание воды и прогресса
• Система достижений

🎯 Для кого:
Для всех, кто хочет улучшить форму, похудеть или набрать мышечную массу с помощью профессионального подхода.

💰 Стоимость: {sub_info['rubles']} ₽ / {sub_info['stars']} Stars
⏰ Срок действия: {days_text.get(subscription_key, subscription_key)}

💳 Выберите способ оплаты:"""

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_") and ("_stars" in data or "_rub" in data):
        # Обработка оплаты с выбранным способом
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        if "_stars" in data:
            subscription_key = data.replace("buy_", "").replace("_stars", "")
            payment_method = "stars"
        else:
            subscription_key = data.replace("buy_", "").replace("_rub", "")
            payment_method = "rub"

        if subscription_key not in SUBSCRIPTION_PRICES:
            await query.answer("❌ Неверный тип подписки")
            return

        sub_info = SUBSCRIPTION_PRICES[subscription_key]
        days_text = {
            "1_day": "1 день",
            "7_days": "7 дней",
            "14_days": "14 дней"
        }
        title = f"Подписка: {days_text.get(subscription_key, subscription_key)}"
        description = f"Доступ ко всем функциям бота на {sub_info['days']} дн."

        if payment_method == "stars":
            # Оплата через Telegram Stars
            payload = f"{user_id}:{subscription_key}:stars"
            prices = [LabeledPrice(label=title, amount=sub_info['stars'])]

            await context.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token="",
                currency="XTR",
                prices=prices
            )
            await query.answer("✅ Инвойс Telegram Stars отправлен!")
        else:
            # Оплата через ЮKassa или ручная оплата
            amount = sub_info['rubles']

            # Проверяем наличие ключей ЮKassa
            from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

            if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
                # Создаем платеж в ЮKassa
                payment_data = YooKassaHandler.create_payment(
                    amount=amount,
                    description=description,
                    user_id=user_id,
                    subscription_key=subscription_key
                )

                if payment_data:
                    # Сохраняем информацию о платеже
                    store_pending_payment(user_id, payment_data['id'], subscription_key)

                    keyboard = [
                        [InlineKeyboardButton("💳 Оплатить", url=payment_data['confirmation_url'])],
                        [InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_payment_{payment_data['id']}")],
                        [InlineKeyboardButton(t("back", lang), callback_data="payment")]
                    ]

                    message = f"""💳 ОПЛАТА БАНКОВСКОЙ КАРТОЙ

🏢 Продавец: AI Fitness Coach Bot
📱 Поддержка: @ProSportRBKSupport

📦 Услуга: {title}
💰 Сумма: {amount} ₽

📋 Что вы получаете:
✅ Полный доступ к AI-тренеру
✅ Персональные планы питания и тренировок
✅ База из 250+ рецептов
✅ Трекинг прогресса
✅ Поддержка 24/7

🔒 Безопасная оплата через ЮKassa
💳 Принимаем все банковские карты

👇 Нажмите "Оплатить" для перехода к оплате
⏱ После оплаты нажмите "Проверить оплату" для активации"""

                    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
                    await query.answer("✅ Платеж создан!")
                else:
                    keyboard = [
                        [InlineKeyboardButton(t("back", lang), callback_data="payment")]
                    ]
                    await query.edit_message_text(
                        "❌ Ошибка создания платежа. Попробуйте позже или свяжитесь с поддержкой.",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    await query.answer("❌ Ошибка создания платежа")
            else:
                # Ручная оплата через администратора
                keyboard = [
                    [InlineKeyboardButton("💬 Написать администратору", url="https://t.me/ProSportRBK")],
                    [InlineKeyboardButton(t("back", lang), callback_data="payment")]
                ]

                message = f"""💳 ОПЛАТА ЧЕРЕЗ АДМИНИСТРАТОРА

🏢 Продавец: AI Fitness Coach Bot
📱 Поддержка: @ProSportRBKSupport

📦 Услуга: {title}
💰 Сумма: {amount} ₽

📋 Что вы получаете:
✅ Полный доступ к AI-тренеру
✅ Персональные планы питания и тренировок
✅ База из 250+ рецептов
✅ Трекинг прогресса и достижений
✅ Поддержка 24/7

🎯 Назначение услуги:
Персональное сопровождение фитнес-целей с помощью искусственного интеллекта для достижения максимальных результатов.

📞 Инструкция по оплате:
1. Нажмите "Написать администратору"
2. Сообщите ваш ID: {user_id}
3. Укажите тариф: {title}
4. Администратор предоставит реквизиты
5. После оплаты подписка активируется автоматически"""

                await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
                await query.answer("💬 Свяжитесь с администратором")

    elif data.startswith("buy_"):
        subscription_key = data.replace("buy_", "")
        if subscription_key not in SUBSCRIPTION_PRICES:
            await query.answer("❌ Неверный тип подписки")
            return
        
        sub_info = SUBSCRIPTION_PRICES[subscription_key]
        title = f"Подписка: {sub_info['title']}"
        description = f"Доступ ко всем функциям бота на {sub_info['days']} дн."
        payload = f"{user_id}:{subscription_key}"
        prices = [LabeledPrice(label=title, amount=sub_info['stars'])]
        
        await context.bot.send_invoice(chat_id=user_id, title=title, description=description,
                                      payload=payload, provider_token="", currency="XTR", prices=prices)
        await query.answer("✅ Инвойс отправлен!")

    elif data.startswith("check_payment_"):
        # Проверка статуса платежа ЮKassa
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        payment_id = data.replace("check_payment_", "")

        # Получаем информацию о платеже
        payment_info = get_pending_payment(payment_id)

        if not payment_info:
            await query.answer("❌ Платеж не найден")
            return

        # Проверяем статус в ЮKassa
        if YooKassaHandler.is_payment_successful(payment_id):
            subscription_key = payment_info['subscription_key']
            sub_info = SUBSCRIPTION_PRICES.get(subscription_key)

            if sub_info:
                # Активируем подписку
                days = sub_info['days']
                subscription_end = datetime.now() + timedelta(days=days)

                db.update_user(user_id, {
                    "subscription_end": subscription_end.isoformat(),
                    "last_payment_date": datetime.now().isoformat(),
                    "total_payments": db.get_user(user_id).get("total_payments", 0) + sub_info['rubles']
                })

                # Удаляем платеж из ожидающих
                remove_pending_payment(payment_id)

                success_message = f"""✅ Оплата прошла успешно!

🎉 Подписка активирована на {days} дн.
📅 Действует до: {subscription_end.strftime('%d.%m.%Y')}

Теперь вам доступны все функции бота!"""

                keyboard = [[InlineKeyboardButton(t("return_menu", lang), callback_data="main_menu")]]
                await query.edit_message_text(success_message, reply_markup=InlineKeyboardMarkup(keyboard))
                await query.answer("✅ Подписка активирована!")
            else:
                await query.answer("❌ Ошибка активации подписки")
        else:
            # Платеж еще не прошел
            await query.answer("⏳ Платеж еще не обработан. Попробуйте через минуту.", show_alert=True)

    elif data == "referrals":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        ref_code = user.get("referral_code", f"REF{user_id}")
        bot = context.bot
        bot_me = await bot.get_me()
        ref_link = f"https://t.me/{bot_me.username}?start={ref_code}"

        referrals_count = sum(1 for u in db.data["users"].values() if u.get("referred_by") == user_id)
        paid_referrals = sum(1 for u in db.data["users"].values() if u.get("referred_by") == user_id and u.get("subscription_end"))

        ref_text = f"""{t('referral_program_title', lang)}

{t('referral_how_works', lang)}
{t('referral_step1', lang)}
{t('referral_step2', lang)}
{t('referral_step3', lang)}

{t('your_referral_link', lang)}
{ref_link}

{t('referral_statistics', lang)}
{t('friends_invited', lang)} {referrals_count}
{t('friends_paid', lang)} {paid_referrals}
{t('bonus_days', lang)} {user.get('bonus_days', 0)}"""

        keyboard = [[InlineKeyboardButton(t("back", lang), callback_data="main_menu")]]
        await query.edit_message_text(ref_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "instructions":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        instr_text = f"""{t('instructions_title', lang)}

{t('instructions_main_menu', lang)}

{t('instructions_profile', lang)}

{t('instructions_results', lang)}

{t('instructions_daily_program', lang)}

{t('instructions_tip', lang)}

{t('instructions_referrals', lang)}

{t('instructions_subscription', lang)}"""

        keyboard = [[InlineKeyboardButton(t("back", lang), callback_data="main_menu")]]
        await query.edit_message_text(instr_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "contacts":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        contacts_text = f"{t('contacts_title', lang)}\n\n{t('contacts_channel', lang)}\nhttps://t.me/ProSportRBK\n\n{t('contacts_support', lang)}"
        await query.edit_message_text(contacts_text,
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("back", lang), callback_data="main_menu")]]))
    
    elif data == "admin_menu":
        if user_id not in ADMIN_IDS:
            return
        await query.edit_message_text(t("admin_panel_title", "ru"), reply_markup=get_admin_menu())
    
    elif data == "admin_stats":
        if user_id not in ADMIN_IDS:
            return
        stats = db.get_stats()
        now = datetime.now()
        new_users_24h = sum(1 for user in db.data["users"].values() if (now - datetime.fromisoformat(user["registration_date"])).days < 1)
        active_subs = sum(1 for user in db.data["users"].values() if db.has_active_subscription(int(user["user_id"])))
        trial_users = sum(1 for user in db.data["users"].values() if user.get("trial_end") and datetime.now() < datetime.fromisoformat(user["trial_end"]) and not user.get("subscription_end"))
        
        stats_text = f"""📊 СТАТИСТИКА БОТА

Пользователи:
- Всего: {stats['total_users']}
- Новых за 24ч: {new_users_24h}

Подписки:
- Активных платных: {active_subs}
- На пробном периоде: {trial_users}

Конверсия:
- Trial → Paid: {round(active_subs / stats['total_users'] * 100, 1) if stats['total_users'] > 0 else 0}%"""
        
        await query.edit_message_text(stats_text, reply_markup=get_admin_menu())
    
    elif data == "admin_users":
        if user_id not in ADMIN_IDS:
            return
        users_list = []
        for uid, user_data in list(db.data["users"].items())[:20]:
            username = user_data.get("username", "No username")
            status = "✅" if db.has_active_subscription(int(uid)) else "❌"
            users_list.append(f"{status} @{username} (ID: {uid})")
        
        users_text = f"""👥 ПОСЛЕДНИЕ ПОЛЬЗОВАТЕЛИ\n\n""" + "\n".join(users_list)
        await query.edit_message_text(users_text, reply_markup=get_admin_menu())
    
    elif data == "admin_broadcast":
        if user_id not in ADMIN_IDS:
            return
        await query.edit_message_text(t("broadcast_prompt", "ru"))
        context.user_data["admin_broadcast"] = True
    
    elif data == "admin_settings":
        if user_id not in ADMIN_IDS:
            return
        target_cals = settings.data["target_calories"]
        settings_text = f"""⚙️ НАСТРОЙКИ БОТА

Целевые калории:
- Похудение: {target_cals['lose_weight']['min']}-{target_cals['lose_weight']['max']} ккал
- Набор массы: {target_cals['gain_muscle']['min']}-{target_cals['gain_muscle']['max']} ккал
- Поддержание: {target_cals['maintain']} ккал

Коэффициенты активности:
- Новичок: {settings.data['activity_levels']['beginner']}
- Средний: {settings.data['activity_levels']['intermediate']}
- Продвинутый: {settings.data['activity_levels']['advanced']}

Цены подписок:
- 1 день: {SUBSCRIPTION_PRICES['1_day']['stars']} Stars
- 7 дней: {SUBSCRIPTION_PRICES['7_days']['stars']} Stars
- 14 дней: {SUBSCRIPTION_PRICES['14_days']['stars']} Stars

Выберите что хотите настроить:"""
        
        await query.edit_message_text(settings_text, reply_markup=get_admin_settings_menu())
    
    elif data == "edit_target_cals":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        await query.edit_message_text("""📊 РЕДАКТИРОВАНИЕ ЦЕЛЕВЫХ КАЛОРИЙ

Отправьте данные в формате:
похудение_мин похудение_макс набор_мин набор_макс поддержание

Пример:
1900 2000 2600 2700 2400

Текущие значения:
Похудение: 1900-2000
Набор: 2600-2700
Поддержание: 2400""", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "target_cals"
    
    elif data == "edit_activity":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        await query.edit_message_text("""📊 РЕДАКТИРОВАНИЕ КОЭФФИЦИЕНТОВ

Отправьте данные в формате:
новичок средний продвинутый

Пример:
1.375 1.55 1.725

Текущие значения:
Новичок: 1.375
Средний: 1.55
Продвинутый: 1.725""", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "activity"
    
    elif data == "edit_prices":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        current_prices = f"""💳 РЕДАКТИРОВАНИЕ ЦЕН ПОДПИСОК

Отправьте данные в формате:
1день 7дней 14дней

Пример:
50 300 500

Текущие цены в Stars:
1 день: {SUBSCRIPTION_PRICES['1_day']['stars']}
7 дней: {SUBSCRIPTION_PRICES['7_days']['stars']}
14 дней: {SUBSCRIPTION_PRICES['14_days']['stars']}"""
        await query.edit_message_text(current_prices, reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "prices"
    
    elif data == "edit_prompt_nutrition":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        await query.edit_message_text(t("nutrition_prompt_title", "ru"), reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "prompt_nutrition"
    
    elif data == "edit_prompt_workout":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        await query.edit_message_text(t("workout_prompt_title", "ru"), reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "prompt_workout"
    
    elif data == "edit_prompt_tips":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_settings")]]
        await query.edit_message_text(t("tip_prompt_title", "ru"), reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["editing"] = "prompt_tips"
    
    elif data == "admin_save_settings":
        if user_id not in ADMIN_IDS:
            return
        settings.save()
        await query.answer(t("settings_saved", "ru"))
        await query.edit_message_text(t("settings_saved", "ru"), reply_markup=get_admin_settings_menu())

    elif data == "admin_knowledge":
        if user_id not in ADMIN_IDS:
            return
        # Загружаем базу знаний
        knowledge_file = "data/knowledge_base.json"
        if os.path.exists(knowledge_file):
            with open(knowledge_file, "r", encoding="utf-8") as f:
                knowledge = json.load(f)
        else:
            knowledge = []

        count = len(knowledge)
        kb_text = t("knowledge_list_title", "ru").format(count=count) + "\n\n"
        if knowledge:
            for i, item in enumerate(knowledge[:10], 1):  # Показываем первые 10
                kb_text += f"{i}. [{item.get('category', 'общее')}] {item.get('text', '')[:50]}...\n"
        else:
            kb_text = t("knowledge_empty", "ru")

        keyboard = [
            [InlineKeyboardButton(t("btn_add_knowledge", "ru"), callback_data="add_knowledge")],
            [InlineKeyboardButton(t("btn_back_menu", "ru"), callback_data="admin_menu")]
        ]
        await query.edit_message_text(kb_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "add_knowledge":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_knowledge")]]
        await query.edit_message_text(t("knowledge_add_prompt", "ru"), reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["adding_knowledge"] = True

    elif data == "admin_ai_training":
        if user_id not in ADMIN_IDS:
            return
        # Загружаем данные обучения
        training_file = "data/training_data.json"
        if os.path.exists(training_file):
            with open(training_file, "r", encoding="utf-8") as f:
                training_data = json.load(f)
        else:
            training_data = []

        count = len(training_data)
        training_text = t("training_data_title", "ru").format(count=count)

        keyboard = [
            [InlineKeyboardButton(t("train_on_examples", "ru"), callback_data="add_training")],
            [InlineKeyboardButton(t("view_training_data", "ru"), callback_data="view_training")],
            [InlineKeyboardButton(t("clear_training", "ru"), callback_data="clear_training")],
            [InlineKeyboardButton(t("btn_back_menu", "ru"), callback_data="admin_menu")]
        ]
        await query.edit_message_text(training_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "add_training":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [[InlineKeyboardButton(t("btn_cancel", "ru"), callback_data="admin_ai_training")]]
        await query.edit_message_text(t("training_example_prompt", "ru"), reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["adding_training"] = True

    elif data == "view_training":
        if user_id not in ADMIN_IDS:
            return
        training_file = "data/training_data.json"
        if os.path.exists(training_file):
            with open(training_file, "r", encoding="utf-8") as f:
                training_data = json.load(f)
            training_text = "📊 ДАННЫЕ ОБУЧЕНИЯ\n\n"
            for i, item in enumerate(training_data[:5], 1):  # Показываем первые 5
                training_text += f"{i}. Q: {item.get('question', '')[:40]}...\nA: {item.get('answer', '')[:40]}...\n\n"
        else:
            training_text = "Нет данных обучения"

        keyboard = [[InlineKeyboardButton(t("btn_back_menu", "ru"), callback_data="admin_ai_training")]]
        await query.edit_message_text(training_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "clear_training":
        if user_id not in ADMIN_IDS:
            return
        training_file = "data/training_data.json"
        with open(training_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        await query.answer(t("training_cleared", "ru"))
        await query.edit_message_text(t("training_cleared", "ru"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="admin_ai_training")]]))

    elif data.startswith("meals_"):
        meals_map = {
            "meals_3": {"count": "3 основных приема", "structure": "завтрак, обед, ужин (БЕЗ перекусов)"},
            "meals_4": {"count": "4-5 равномерных приемов", "structure": "4-5 равных по размеру приёмов пищи в течение дня"},
            "meals_5": {"count": "3 основных + 2 перекуса", "structure": "завтрак, перекус, обед, перекус, ужин"}
        }
        selected = meals_map.get(data, meals_map["meals_5"])
        context.user_data["nutrition_data"]["meals_count"] = selected["count"]
        context.user_data["nutrition_data"]["meals_structure"] = selected["structure"]
        
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        keyboard = [
            [InlineKeyboardButton(t("cook_full", lang), callback_data="cook_full")],
            [InlineKeyboardButton(t("cook_min", lang), callback_data="cook_min")],
            [InlineKeyboardButton(t("cook_none", lang), callback_data="cook_none")]
        ]
        await query.edit_message_text(t("nutrition_q6", lang), reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("cook_"):
        time_map = {
            "cook_full": "Полноценная готовка (плита, духовка)",
            "cook_min": "Минимальная готовка (микроволновка, варка)",
            "cook_none": "Только готовые продукты (без готовки)"
        }
        context.user_data["nutrition_data"]["cooking_time"] = time_map.get(data, "среднее")

        # Красивая анимация создания плана
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        loading_msg = await query.edit_message_text(t("generating_nutrition", lang))

        # Запускаем красивую анимацию
        await animated_loading(loading_msg, lang)

        profile = user.get("profile", {})
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                nutrition_plan = AIGenerator.generate_nutrition_plan(profile, context.user_data["nutrition_data"], user_id=user_id)
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА КАЧЕСТВА
                validation = validate_ai_response(nutrition_plan, "nutrition")
                
                if not validation["valid"]:
                    logger.warning(f"Попытка {attempt + 1}: {validation['reason']}")
                    if attempt < max_attempts - 1:
                        continue
                    else:
                        # Последняя попытка не удалась
                        await loading_msg.edit_text(
                            f"❌ Не удалось создать качественный план питания.\n"
                            f"Причина: {validation['reason']}\n\n"
                            "Пожалуйста, попробуйте ещё раз.",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(t("btn_try_again", lang), callback_data="nutrition_plan"),
                                InlineKeyboardButton(t("btn_back_menu", lang), callback_data="main_menu")
                            ]])
                        )
                        return
                
                # План валиден, используем очищенный текст
                nutrition_plan = validation["text"]
                context.user_data["current_plan"] = nutrition_plan
                context.user_data["last_plan_type"] = "nutrition"
                
                # Парсим калории
                parsed_cals = parse_calories_from_text(nutrition_plan)
                calories = calculate_calories(profile)
                
                # ПРОВЕРКА: Если калории не распознаны или сильно отличаются
                if parsed_cals == 0:
                    logger.warning(f"Не удалось распознать калории в плане (попытка {attempt + 1})")
                    if attempt < max_attempts - 1:
                        continue
                    else:
                        # Используем целевые калории как fallback
                        parsed_cals = calories['daily_calories']
                        logger.warning(f"Использую целевые калории: {parsed_cals}")
                
                # Сохраняем калории
                if parsed_cals > 0:
                    save_daily_results(user_id, parsed_cals, 0)

                # Начисляем достижение за план питания
                achievement_msg = check_and_award_achievements(user_id, "nutrition")

                # Применяем финальную очистку
                safe_plan = final_clean_text(nutrition_plan)

                keyboard = [
                    [InlineKeyboardButton(t("regenerate_button", lang), callback_data="regenerate_nutrition")],
                    [InlineKeyboardButton(t("back_button", lang), callback_data="main_menu")]
                ]
                
                # Отправляем план
                if len(safe_plan) > 3500:
                    parts = [safe_plan[i:i+3500] for i in range(0, len(safe_plan), 3500)]
                    await loading_msg.edit_text(parts[0])
                    for part in parts[1:]:
                        await query.message.reply_text(part)
                    if achievement_msg:
                        await query.message.reply_text(achievement_msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    else:
                        await query.message.reply_text("✅ План готов!", reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    final_message = safe_plan
                    if achievement_msg:
                        final_message += f"\n\n{achievement_msg}"
                    await loading_msg.edit_text(
                        final_message,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                
                # Удаляем временные данные
                if "nutrition_step" in context.user_data:
                    del context.user_data["nutrition_step"]
                if "nutrition_data" in context.user_data:
                    del context.user_data["nutrition_data"]
                
                return  # Успешно завершили
                
            except Exception as e:
                logger.error(f"Ошибка генерации плана питания (попытка {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    await loading_msg.edit_text(
                        "❌ Произошла ошибка при генерации плана.\n"
                        "Пожалуйста, попробуйте ещё раз через несколько секунд.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔄 Попробовать снова", callback_data="nutrition_plan"),
                            InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")
                        ]])
                    )
    
    elif data.startswith("time_"):
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        time_map = {"time_30": "30 минут", "time_60": "45-60 минут", "time_90": "1.5 часа"}
        context.user_data["workout_data"]["duration"] = time_map.get(data, "45-60 минут")

        keyboard = [
            [InlineKeyboardButton(t("energy_high", lang), callback_data="energy_high")],
            [InlineKeyboardButton(t("energy_medium", lang), callback_data="energy_medium")],
            [InlineKeyboardButton(t("energy_low", lang), callback_data="energy_low")],
            [InlineKeyboardButton(t("energy_recovery", lang), callback_data="energy_recovery")]
        ]
        await query.edit_message_text(t("workout_q4", lang),
                                     reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("energy_"):
        energy_map = {
            "energy_high": "high",
            "energy_medium": "medium",
            "energy_low": "low",
            "energy_recovery": "recovery"
        }
        intensity = energy_map.get(data, "medium")
        context.user_data["workout_data"]["energy_level"] = intensity
        
        # Красивая анимация генерации
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        loading_msg = await query.edit_message_text(t("generating_workout", lang))

        # Запускаем анимацию
        await animated_workout_loading(loading_msg, lang)

        profile = user.get("profile", {})
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                workout_plan = AIGenerator.generate_workout_plan(profile, context.user_data["workout_data"], user_id=user_id)
                
                # КРИТИЧЕСКАЯ ПРОВЕРКА КАЧЕСТВА
                validation = validate_ai_response(workout_plan, "workout")
                
                if not validation["valid"]:
                    logger.warning(f"Попытка {attempt + 1}: {validation['reason']}")
                    if attempt < max_attempts - 1:
                        continue
                    else:
                        await loading_msg.edit_text(
                            f"❌ Не удалось создать качественную тренировку.\n"
                            f"Причина: {validation['reason']}\n\n"
                            "Пожалуйста, попробуйте ещё раз.",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(t("btn_try_again", lang), callback_data="workout_plan"),
                                InlineKeyboardButton(t("btn_back_menu", lang), callback_data="main_menu")
                            ]])
                        )
                        return
                
                # План валиден
                workout_plan = validation["text"]
                context.user_data["current_plan"] = workout_plan
                context.user_data["last_plan_type"] = "workout"
                
                # Парсим калории
                workout_cals = parse_workout_calories(workout_plan)
                
                # Если не распознали, рассчитываем вручную
                if workout_cals == 0:
                    weight = profile.get("weight", 70)
                    duration = context.user_data["workout_data"].get("duration", "45-60 минут")
                    workout_cals = calculate_workout_calories(weight, duration, intensity)
                    logger.warning(f"Калории не распознаны, рассчитано: {workout_cals}")
                
                # Сохраняем калории
                if workout_cals > 0:
                    save_daily_results(user_id, 0, workout_cals)

                # Сохраняем тренировку в историю для отслеживания прогресса
                workout_data = context.user_data.get("workout_data", {})

                # Парсим длительность из строки (например "45-60 минут" -> 45)
                duration_str = workout_data.get("duration", "45-60")
                try:
                    parsed_duration = int(''.join(filter(str.isdigit, duration_str.split('-')[0])))
                except:
                    parsed_duration = 45

                workout_history_data = {
                    'duration_minutes': parsed_duration,
                    'estimated_calories': workout_cals,
                    'exercises': [],  # Пустой список - упражнения уже в тексте плана
                    'type': workout_data.get('workout_type', 'strength'),
                    'location': workout_data.get('location_equipment', 'gym'),
                    'level': profile.get('level', 'intermediate')
                }
                workouts_loader.save_workout_to_history(user_id, workout_history_data)

                # Начисляем достижение за тренировку
                achievement_msg = check_and_award_achievements(user_id, "workout")

                # Формируем итоговое сообщение на языке пользователя
                if lang == "ru":
                    completion_text = f"""

─────────────────────────
✅ ТРЕНИРОВКА ГОТОВА!

⏱ Длительность: {context.user_data["workout_data"].get("duration", "45-60 минут")}
🔥 Расход калорий: ~{workout_cals} ккал
⚡ Ваш уровень энергии: {intensity}

💡 Рекомендация: Выпейте воду после тренировки!

🏆 Отличная работа! Вы на пути к своей цели!"""
                elif lang == "en":
                    completion_text = f"""

─────────────────────────
✅ WORKOUT READY!

⏱ Duration: {context.user_data["workout_data"].get("duration", "45-60 min")}
🔥 Calories burned: ~{workout_cals} kcal
⚡ Your energy level: {intensity}

💡 Tip: Drink water after workout!

🏆 Great job! You're on track!"""
                else:
                    completion_text = f"""

─────────────────────────
✅ MASHG'ULOT TAYYOR!

⏱ Davomiyligi: {context.user_data["workout_data"].get("duration", "45-60 daq")}
🔥 Yoqilgan kaloriyalar: ~{workout_cals} kkal
⚡ Energiya darajasi: {intensity}

💡 Tavsiya: Mashg'ulotdan keyin suv iching!

🏆 Ajoyib! Maqsadingizga erishyapsiz!"""
                
                # Применяем финальную очистку
                safe_plan = final_clean_text(workout_plan)

                # Текст для кнопки "Тренировка выполнена!"
                complete_btn_text = {
                    'ru': '✅ Тренировка выполнена!',
                    'en': '✅ Workout completed!',
                    'uz': '✅ Mashg\'ulot bajarildi!'
                }

                keyboard = [
                    [InlineKeyboardButton(complete_btn_text.get(lang, complete_btn_text['ru']), callback_data="workout_complete")],
                    [InlineKeyboardButton(t("regenerate_button", lang), callback_data="regenerate_workout")],
                    [InlineKeyboardButton(t("back_button", lang), callback_data="main_menu")]
                ]
                
                # Отправляем план
                if len(safe_plan) > 3500:
                    parts = [safe_plan[i:i+3500] for i in range(0, len(safe_plan), 3500)]
                    await loading_msg.edit_text(f"{parts[0]}")
                    for part in parts[1:]:
                        await query.message.reply_text(part)
                    final_text = completion_text
                    if achievement_msg:
                        final_text += f"\n\n{achievement_msg}"
                    await query.message.reply_text(final_text, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    final_message = f"{safe_plan}{completion_text}"
                    if achievement_msg:
                        final_message += f"\n\n{achievement_msg}"
                    await loading_msg.edit_text(final_message, reply_markup=InlineKeyboardMarkup(keyboard))
                
                # Удаляем временные данные
                if "workout_step" in context.user_data:
                    del context.user_data["workout_step"]
                if "workout_data" in context.user_data:
                    del context.user_data["workout_data"]
                
                return  # Успешно завершили
                
            except Exception as e:
                logger.error(f"Ошибка генерации тренировки (попытка {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    await loading_msg.edit_text(
                        "❌ Произошла ошибка при генерации тренировки.\n"
                        "Пожалуйста, попробуйте ещё раз через несколько секунд.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔄 Попробовать снова", callback_data="workout_plan"),
                            InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")
                        ]])
                    )
    
    elif data == "revise_plan":
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"

        # Определяем тип последнего плана
        last_plan_type = context.user_data.get("last_plan_type")

        # КРИТИЧЕСКИ ВАЖНО: Очищаем ВСЕ старые данные перед переделкой
        if "nutrition_data" in context.user_data:
            del context.user_data["nutrition_data"]
        if "workout_data" in context.user_data:
            del context.user_data["workout_data"]
        if "current_plan" in context.user_data:
            del context.user_data["current_plan"]

        if last_plan_type == "nutrition":
            # Повторно запрашиваем план питания С НУЛЯ
            await query.edit_message_text(t("nutrition_question_1", lang))
            context.user_data["nutrition_step"] = 1
            context.user_data["nutrition_data"] = {}
        else:
            # Повторно запрашиваем план тренировки С НУЛЯ
            keyboard = [
                [InlineKeyboardButton(t("chest", lang), callback_data="muscle_chest")],
                [InlineKeyboardButton(t("back_muscles", lang), callback_data="muscle_back")],
                [InlineKeyboardButton(t("legs", lang), callback_data="muscle_legs")],
                [InlineKeyboardButton(t("full_body", lang), callback_data="muscle_full_body")],
                [InlineKeyboardButton(t("cardio", lang), callback_data="muscle_cardio")]
            ]
            await query.edit_message_text(t("workout_selection", lang),
                                         reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data["workout_step"] = 0
            context.user_data["workout_data"] = {}
    
    elif data == "ask_question":
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        question_text = f"{t('ask_question_title', lang)}\n\n{t('ask_question_prompt', lang)}"
        await query.edit_message_text(question_text)
        context.user_data["awaiting_question"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Обработка режима чата с нейросетью
    user = db.get_user(user_id)
    if user and user.get("chat_mode", False):
        lang = user.get("language", "ru")

        # Добавляем сообщение в историю
        if "chat_history" not in user:
            user["chat_history"] = []

        user["chat_history"].append({"role": "user", "content": text})

        # Ограничиваем историю последними 10 сообщениями
        if len(user["chat_history"]) > 20:
            user["chat_history"] = user["chat_history"][-20:]

        db.update_user(user_id, user)

        # Отправляем запрос к AI
        try:
            # Формируем системный промпт
            system_prompt = {
                "ru": "Ты дружелюбный AI-ассистент фитнес-бота. Помогай пользователям с вопросами о фитнесе, питании, здоровье и мотивации. Отвечай кратко и по делу, но дружелюбно.",
                "en": "You are a friendly AI assistant for a fitness bot. Help users with questions about fitness, nutrition, health and motivation. Answer briefly and to the point, but friendly.",
                "uz": "Siz fitness bot uchun do'stona AI yordamchisisiz. Foydalanuvchilarga fitness, ovqatlanish, salomatlik va motivatsiya haqidagi savollar bilan yordam bering. Qisqa va aniq javob bering, lekin do'stona."
            }

            # Формируем сообщения для API
            messages = [{"role": "system", "content": system_prompt.get(lang, system_prompt["ru"])}]
            messages.extend(user["chat_history"])

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            ai_response = response.json()["choices"][0]["message"]["content"]

            # Добавляем ответ в историю
            user["chat_history"].append({"role": "assistant", "content": ai_response})
            db.update_user(user_id, user)

            # Отправляем ответ с кнопкой завершения разговора
            keyboard = [[InlineKeyboardButton("🚪 Завершить разговор", callback_data="end_ai_chat")]]
            await update.message.reply_text(ai_response, reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as e:
            logger.error(f"AI chat error: {e}")
            error_msg = {
                "ru": "❌ Произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.",
                "en": "❌ An error occurred while processing your message. Please try again.",
                "uz": "❌ Xabaringizni qayta ishlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            }
            keyboard = [[InlineKeyboardButton("🚪 Завершить разговор", callback_data="end_ai_chat")]]
            await update.message.reply_text(error_msg.get(lang, error_msg["ru"]), reply_markup=InlineKeyboardMarkup(keyboard))

        return

    # Обработка добавления знаний
    if "adding_knowledge" in context.user_data:
        if user_id not in ADMIN_IDS:
            return
        try:
            # Формат: Категория | Текст
            if "|" in text:
                category, knowledge_text = text.split("|", 1)
                category = category.strip()
                knowledge_text = knowledge_text.strip()
            else:
                category = "общее"
                knowledge_text = text

            # Загружаем или создаем базу знаний
            knowledge_file = "data/knowledge_base.json"
            os.makedirs("data", exist_ok=True)

            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    knowledge = json.load(f)
            else:
                knowledge = []

            # Добавляем новое знание
            knowledge.append({
                "category": category,
                "text": knowledge_text,
                "added_by": user_id,
                "timestamp": datetime.now().isoformat()
            })

            # Сохраняем
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)

            del context.user_data["adding_knowledge"]
            await update.message.reply_text(t("knowledge_added", "ru"),
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_to_knowledge", "ru"), callback_data="admin_knowledge")]]))
        except Exception as e:
            logger.error(f"Ошибка добавления знания: {e}")
            await update.message.reply_text("❌ Ошибка сохранения. Попробуйте снова.\n\nПравильный формат:\nКатегория | Текст знания",
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_to_knowledge", "ru"), callback_data="admin_knowledge")]]))
        return

    # Обработка добавления данных обучения
    if "adding_training" in context.user_data:
        if user_id not in ADMIN_IDS:
            return
        try:
            # Формат: ВОПРОС: ... ОТВЕТ: ...
            if "ВОПРОС:" in text and "ОТВЕТ:" in text:
                parts = text.split("ОТВЕТ:")
                question = parts[0].replace("ВОПРОС:", "").strip()
                answer = parts[1].strip()
            elif "QUESTION:" in text and "ANSWER:" in text:
                parts = text.split("ANSWER:")
                question = parts[0].replace("QUESTION:", "").strip()
                answer = parts[1].strip()
            else:
                await update.message.reply_text("❌ Неверный формат. Используйте:\nВОПРОС: текст вопроса\nОТВЕТ: текст ответа",
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_to_ai_training", "ru"), callback_data="admin_ai_training")]]))
                return

            # Загружаем или создаем данные обучения
            training_file = "data/training_data.json"
            os.makedirs("data", exist_ok=True)

            if os.path.exists(training_file):
                with open(training_file, "r", encoding="utf-8") as f:
                    training_data = json.load(f)
            else:
                training_data = []

            # Добавляем новый пример
            training_data.append({
                "question": question,
                "answer": answer,
                "added_by": user_id,
                "timestamp": datetime.now().isoformat()
            })

            # Сохраняем
            with open(training_file, "w", encoding="utf-8") as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)

            del context.user_data["adding_training"]
            await update.message.reply_text(t("training_added", "ru"),
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_to_ai_training", "ru"), callback_data="admin_ai_training")]]))
        except Exception as e:
            logger.error(f"Ошибка добавления обучающих данных: {e}")
            await update.message.reply_text("❌ Ошибка сохранения. Попробуйте снова.\n\nПравильный формат:\nВОПРОС: текст\nОТВЕТ: текст",
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_to_ai_training", "ru"), callback_data="admin_ai_training")]]))
        return

    # Обработка редактирования профиля
    if "editing_profile" in context.user_data:
        field = context.user_data["editing_profile"]
        user = db.get_user(user_id)
        profile = user.get("profile", {})
        
        try:
            if field == "name":
                profile["name"] = text
                db.update_user(user_id, {"profile": profile})
                await update.message.reply_text(t("name_updated", lang),
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("to_profile", lang), callback_data="profile")]]))
            elif field == "age":
                age = int(text)
                if age < 16 or age > 100:
                    await update.message.reply_text(t("age_must_be_range", lang))
                    return
                profile["age"] = age
                db.update_user(user_id, {"profile": profile})
                await update.message.reply_text(t("age_updated", lang),
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("to_profile", lang), callback_data="profile")]]))
            elif field == "height":
                height = int(text)
                if height < 120 or height > 250:
                    await update.message.reply_text(t("height_must_be_range", lang))
                    return
                profile["height"] = height
                db.update_user(user_id, {"profile": profile})
                await update.message.reply_text(t("height_updated", lang),
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("to_profile", lang), callback_data="profile")]]))
            elif field == "weight":
                weight = float(text)
                if weight < 35 or weight > 250:
                    await update.message.reply_text(t("weight_must_be_range", lang))
                    return
                profile["weight"] = weight
                db.update_user(user_id, {"profile": profile})
                await update.message.reply_text(t("weight_updated", lang),
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("to_profile", lang), callback_data="profile")]]))
            elif field == "limitations":
                limitations = text if text != "-" else t("none_text", lang)
                profile["limitations"] = limitations
                db.update_user(user_id, {"profile": profile})
                await update.message.reply_text(t("limitations_updated", lang),
                                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("to_profile", lang), callback_data="profile")]]))

            del context.user_data["editing_profile"]
        except ValueError:
            await update.message.reply_text(t("input_error", lang))
        return
    
    if "editing" in context.user_data:
        editing_type = context.user_data["editing"]
        
        if editing_type == "target_cals":
            try:
                parts = text.split()
                if len(parts) == 5:
                    settings.data["target_calories"]["lose_weight"]["min"] = int(parts[0])
                    settings.data["target_calories"]["lose_weight"]["max"] = int(parts[1])
                    settings.data["target_calories"]["gain_muscle"]["min"] = int(parts[2])
                    settings.data["target_calories"]["gain_muscle"]["max"] = int(parts[3])
                    settings.data["target_calories"]["maintain"] = int(parts[4])
                    settings.save()
                    del context.user_data["editing"]
                    await update.message.reply_text(t("target_calories_updated", "ru"), reply_markup=get_admin_settings_menu())
                else:
                    await update.message.reply_text(t("invalid_format_need_5_numbers", "ru"))
            except ValueError:
                await update.message.reply_text(t("invalid_format_need_3_numbers", "ru"))
        
        elif editing_type == "activity":
            try:
                parts = text.split()
                if len(parts) == 3:
                    settings.data["activity_levels"]["beginner"] = float(parts[0])
                    settings.data["activity_levels"]["intermediate"] = float(parts[1])
                    settings.data["activity_levels"]["advanced"] = float(parts[2])
                    settings.save()
                    del context.user_data["editing"]
                    await update.message.reply_text(t("coefficients_updated", "ru"), reply_markup=get_admin_settings_menu())
                else:
                    await update.message.reply_text(t("invalid_format_need_3_numbers", "ru"))
            except ValueError:
                await update.message.reply_text(t("input_error", "ru"))

        elif editing_type == "prices":
            try:
                parts = text.split()
                if len(parts) == 3:
                    SUBSCRIPTION_PRICES["1_day"]["stars"] = int(parts[0])
                    SUBSCRIPTION_PRICES["7_days"]["stars"] = int(parts[1])
                    SUBSCRIPTION_PRICES["14_days"]["stars"] = int(parts[2])

                    # Сохраняем цены в настройки
                    if "subscription_prices" not in settings.data:
                        settings.data["subscription_prices"] = {}
                    settings.data["subscription_prices"] = {
                        "1_day": {"stars": int(parts[0]), "days": 1, "title": "1 день"},
                        "7_days": {"stars": int(parts[1]), "days": 7, "title": "7 дней"},
                        "14_days": {"stars": int(parts[2]), "days": 14, "title": "14 дней"}
                    }
                    settings.save()
                    del context.user_data["editing"]
                    await update.message.reply_text(t("prices_updated", "ru"), reply_markup=get_admin_settings_menu())
                else:
                    await update.message.reply_text(t("invalid_format_need_3_numbers", "ru"))
            except ValueError:
                await update.message.reply_text(t("input_error", "ru"))

        elif editing_type.startswith("prompt_"):
            prompts = settings.get_prompts()
            prompt_key = editing_type.replace("prompt_", "") + "_system"
            prompts[prompt_key] = text

            with open("prompts.json", "w", encoding="utf-8") as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)

            del context.user_data["editing"]
            await update.message.reply_text(t("prompt_updated", "ru"), reply_markup=get_admin_settings_menu())
        
        return
    
    if "nutrition_step" in context.user_data:
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        step = context.user_data["nutrition_step"]

        if step == 1:
            context.user_data["nutrition_data"]["available_products"] = text
            await update.message.reply_text(t("nutrition_q2", lang))
            context.user_data["nutrition_step"] = 2
        elif step == 2:
            context.user_data["nutrition_data"]["exclude"] = text if text != "-" else t("none_text", lang)

            # Сразу генерируем план, пропускаем вопросы 3,4,5
            context.user_data["nutrition_data"]["meals_per_day"] = "3"
            nutrition_data = context.user_data["nutrition_data"]
            del context.user_data["nutrition_step"]
            del context.user_data["nutrition_data"]

            user = db.get_user(user_id)
            profile = user.get("profile", {})

            loading_msg = await update.message.reply_text(t("generating_plan", lang))
            await animated_loading(loading_msg, lang)

            plan = AIGenerator.generate_nutrition_plan(profile, nutrition_data, lang, user_id)

            safe_plan = final_clean_text(plan)

            # Загружаем план на Telegraph и создаем Web App кнопку
            user = db.get_user(user_id)
            keyboard = []

            logger.info(f"Проверка Telegraph: user={user is not None}, last_plan_html={user.get('last_plan_html') if user else None}")

            if user and user.get('last_plan_html'):
                try:
                    # Отправляем HTML как документ
                    with open(user['last_plan_html'], 'rb') as f:
                        doc_caption = {
                            'ru': '📱 Ваш план готов!\n\n💡 Откройте файл в браузере или любом устройстве для красивого просмотра.',
                            'en': '📱 Your plan is ready!\n\n💡 Open the file in browser or any device for beautiful view.',
                            'uz': '📱 Rejangiz tayyor!\n\n💡 Chiroyli ko\'rish uchun faylni brauzerda oching.'
                        }

                        await update.message.reply_document(
                            document=f,
                            filename='nutrition_plan.html',
                            caption=doc_caption.get(lang, doc_caption['ru'])
                        )

                    logger.info(f"✅ HTML план отправлен как файл")

                except Exception as e:
                    logger.error(f"❌ Ошибка отправки файла: {e}")
                    import traceback
                    logger.error(traceback.format_exc())

            keyboard.append([InlineKeyboardButton(t("regenerate_button", lang), callback_data="regenerate_nutrition")])
            keyboard.append([InlineKeyboardButton(t("back_button", lang), callback_data="main_menu")])

            plan_ready_text = {
                'ru': '✅ Ваш план питания готов!\n\n📱 Нажмите кнопку ниже для просмотра.',
                'en': '✅ Your nutrition plan is ready!\n\n📱 Click the button below to view.',
                'uz': '✅ Ovqatlanish rejangiz tayyor!\n\n📱 Ko\'rish uchun quyidagi tugmani bosing.'
            }

            await loading_msg.edit_text(
                plan_ready_text.get(lang, plan_ready_text['ru']),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return
    
    if "workout_step" in context.user_data:
        user = db.get_user(user_id)
        lang = user.get("language", "ru") if user else "ru"
        step = context.user_data["workout_step"]

        if step == 1:
            context.user_data["workout_data"]["location_equipment"] = text
            keyboard = [
                [InlineKeyboardButton(t("time_30", lang), callback_data="time_30")],
                [InlineKeyboardButton(t("time_60", lang), callback_data="time_60")],
                [InlineKeyboardButton(t("time_90", lang), callback_data="time_90")]
            ]
            await update.message.reply_text(t("workout_q3", lang),
                                          reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data["workout_step"] = 2
        return
    
    if context.user_data.get("awaiting_revision"):
        user = db.get_user(update.effective_user.id)
        lang = user.get("language", "ru")
        await update.message.reply_text(t("regenerating_plan", lang))
        current_plan = context.user_data.get("current_plan", "")
        revision_prompt = f"""У пользователя план:
{current_plan[:1000]}...

Пользователь хочет: {text}

ВАЖНО: ПОЛНОСТЬЮ выполни запрос пользователя БЕЗ ОГРАНИЧЕНИЙ."""
        
        try:
            revised_plan = AIGenerator._call_api(revision_prompt)
            context.user_data["current_plan"] = revised_plan
            del context.user_data["awaiting_revision"]
            
            safe_plan = final_clean_text(revised_plan)
            keyboard = [
                [InlineKeyboardButton("🔄 Переделать план", callback_data="revise_plan")],
                [InlineKeyboardButton("❓ Задать вопрос", callback_data="ask_question")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
            ]
            
            if len(safe_plan) > 3900:
                parts = [safe_plan[i:i+3900] for i in range(0, len(safe_plan), 3900)]
                await update.message.reply_text(f"🔄 ОБНОВЛЕННЫЙ ПЛАН\n\n{parts[0]}")
                for part in parts[1:]:
                    await update.message.reply_text(part)
                await update.message.reply_text("✅ План обновлен!", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await update.message.reply_text(f"🔄 ОБНОВЛЕННЫЙ ПЛАН\n\n{safe_plan}", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text("❌ Ошибка при переделке плана. Попробуйте еще раз.")
        return
    
    if context.user_data.get("awaiting_question"):
        await update.message.reply_text("⏳ Обдумываю ответ...")
        user = db.get_user(user_id)
        profile = user.get("profile", {})
        current_plan = context.user_data.get("current_plan", "")
        
        question_prompt = f"""Профиль пользователя:
- Возраст: {profile.get('age')}
- Вес: {profile.get('weight')} кг
- Цель: {profile.get('goal')}
- Уровень: {profile.get('level')}

Текущий план (фрагмент):
{current_plan[:500]}...

Вопрос пользователя: {text}

Дай развернутый, полезный и научно обоснованный ответ."""
        
        try:
            user = db.get_user(user_id)
            lang = user.get("language", "ru")

            answer = AIGenerator._call_api(question_prompt)
            del context.user_data["awaiting_question"]

            safe_answer = final_clean_text(answer)
            keyboard = [
                [InlineKeyboardButton(t("question_back_menu", lang), callback_data="main_menu")]
            ]
            await update.message.reply_text(f"{t('question_answer_title', lang)}\n\n{safe_answer}",
                                          reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            user = db.get_user(user_id)
            lang = user.get("language", "ru")
            logger.error(f"Error: {e}")
            await update.message.reply_text(t("question_error", lang))
        return
    
    if context.user_data.get("admin_broadcast"):
        if user_id not in ADMIN_IDS:
            return
        sent = 0
        failed = 0
        status_message = await update.message.reply_text("📢 Начинаю рассылку...")
        
        for uid in db.data["users"].keys():
            try:
                await context.bot.send_message(int(uid), f"📢 Сообщение от администрации:\n\n{text}")
                sent += 1
            except Exception as e:
                failed += 1
                logger.error(f"Failed to send to {uid}: {e}")
        
        await status_message.edit_text(f"✅ Рассылка завершена!\n\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}")
        del context.user_data["admin_broadcast"]
        return
    
    user = db.get_user(update.effective_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await update.message.reply_text(t("unknown_message", lang), reply_markup=get_main_menu(lang))

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def reset_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для сброса языка (для тестирования)"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if user and "language" in user:
        del user["language"]
        db.update_user(user_id, user)
        await update.message.reply_text("✅ Язык сброшен! Отправьте /start для выбора нового языка.")
    else:
        await update.message.reply_text(t("no_language_set", "ru"))

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload_parts = payment.invoice_payload.split(":")
    user_id = int(payload_parts[0])
    payment_type = payload_parts[1]

    if payment_type == "tip":
        # Обработка покупки совета
        user = db.get_user(user_id)
        lang = user.get("language", "ru")

        loading_messages = {
            "ru": "⏳ Генерирую ваш персональный совет...",
            "en": "⏳ Generating your personal tip...",
            "uz": "⏳ Shaxsiy maslahat yaratyapman..."
        }

        loading_msg = await update.message.reply_text(loading_messages.get(lang, loading_messages["ru"]))
        tip = AIGenerator.generate_tip(user_id=user_id)

        keyboard = [
            [InlineKeyboardButton("⭐ Получить ещё совет за 100 Stars", callback_data="buy_tip")],
            [InlineKeyboardButton("⬅️ В главное меню", callback_data="main_menu")]
        ]

        await loading_msg.edit_text(
            f"💡 ВАШ ПЕРСОНАЛЬНЫЙ СОВЕТ\n\n{tip}\n\n✅ Спасибо за покупку!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # Обработка подписки (только для Telegram Stars, т.к. ЮKassa обрабатывается отдельно)
        # Проверяем есть ли третий параметр ":stars" в payload
        if len(payload_parts) > 2 and payload_parts[2] == "stars":
            subscription_key = payment_type
        else:
            # Старый формат для обратной совместимости
            subscription_key = payment_type

        if subscription_key not in SUBSCRIPTION_PRICES:
            await update.message.reply_text("❌ Ошибка: неверный тип подписки")
            return

        sub_info = SUBSCRIPTION_PRICES[subscription_key]
        db.add_subscription(user_id, sub_info['days'])

        user = db.get_user(user_id)
        if user.get("referred_by"):
            referrer_id = user["referred_by"]
            db.update_user(referrer_id, {"bonus_days": db.get_user(referrer_id).get("bonus_days", 0) + 3})
            await context.bot.send_message(referrer_id, "🎉 Ваш друг оформил подписку!\n\nВы получили +3 бонусных дня! 🎁")
            db.update_user(user_id, {"referred_by": None})

        await update.message.reply_text(
            f"✅ Оплата успешно завершена!\n\nВаша подписка активирована на {sub_info['days']} дн.\n\nТеперь вам доступны все функции бота! 💪",
            reply_markup=get_main_menu())

def main():
    # Запускаем веб-сервер для HTML-планов
    try:
        from web_server import web_server
        if web_server.start():
            logger.info("✅ Веб-сервер для мини-приложений запущен на http://localhost:8000")
        else:
            logger.warning("⚠️ Не удалось запустить веб-сервер")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-сервера: {e}")

    application = Application.builder().token(BOT_TOKEN).build()

    profile_handler = ConversationHandler(
        name="profile_setup",
        entry_points=[CommandHandler("start", start_command)],
        states={
            LANGUAGE_SELECT: [CallbackQueryHandler(language_select, pattern="^lang_")],
            PROFILE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_name)],
            PROFILE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_age)],
            PROFILE_GENDER: [CallbackQueryHandler(profile_gender, pattern="^gender_")],
            PROFILE_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_height)],
            PROFILE_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_weight)],
            PROFILE_GOAL: [CallbackQueryHandler(profile_goal, pattern="^goal_")],
            PROFILE_LEVEL: [CallbackQueryHandler(profile_level, pattern="^level_")],
            PROFILE_LIMITATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_limitations)],
        },
        fallbacks=[CallbackQueryHandler(handle_callback, pattern="^main_menu$"), CommandHandler("start", start_command)],
        allow_reentry=True
    )
    
    application.add_handler(profile_handler)
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("p", quick_test_command))
    application.add_handler(CommandHandler("reset_lang", reset_language_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()