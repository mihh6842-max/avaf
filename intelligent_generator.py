"""
Интеллектуальная система генерации планов питания и тренировок
Работает БЕЗ нейросетей - только логика и базы данных
"""

from typing import Dict, List, Optional
from knowledge_base import NutritionDatabase, RecipeDatabase, ExerciseDatabase
import random


def translate_with_ai(text: str, target_language: str, max_retries: int = 2) -> str:
    """
    Переводит текст с помощью Google Translate (через deep-translator)
    БЕСПЛАТНО и быстро!

    Args:
        text: Текст на русском для перевода
        target_language: Целевой язык (en, uz)
        max_retries: Количество попыток при ошибке

    Returns:
        Переведенный текст
    """
    if target_language == "ru" or not text:
        return text

    try:
        from deep_translator import GoogleTranslator

        lang_map = {"en": "en", "uz": "uz"}
        target = lang_map.get(target_language, "en")

        # Google Translate работает с ограничением ~5000 символов за раз
        # Разбиваем на части если текст большой
        max_chunk_size = 4500

        if len(text) <= max_chunk_size:
            # Переводим сразу
            translator = GoogleTranslator(source='ru', target=target)
            translated = translator.translate(text)

            if translated and len(translated) > 50:
                print(f"[OK] Google Translate: {len(translated)} chars ({target_language})")
                return translated
            else:
                print(f"[WARN] Empty translation from Google")
                return text
        else:
            # Разбиваем на части по абзацам
            parts = text.split('\n\n')
            translated_parts = []

            translator = GoogleTranslator(source='ru', target=target)

            for part in parts:
                if part.strip():
                    try:
                        trans_part = translator.translate(part)
                        translated_parts.append(trans_part if trans_part else part)
                    except:
                        translated_parts.append(part)  # Если часть не перевелась, оставляем оригинал
                else:
                    translated_parts.append(part)

            result = '\n\n'.join(translated_parts)
            print(f"[OK] Google Translate (chunked): {len(result)} chars ({target_language})")
            return result

    except ImportError:
        print(f"[ERROR] deep-translator not installed. Run: pip install deep-translator")
        return text
    except Exception as e:
        print(f"[ERROR] Translation failed: {str(e)}")
        return text


class IntelligentMealPlanner:
    """
    Интеллектуальная система планирования питания
    НЕ использует нейросети - только логику и базы данных
    """

    def __init__(self):
        self.nutrition_db = NutritionDatabase()
        self.recipe_db = RecipeDatabase()
        self.language_templates = self._load_templates()
        self.used_products_history = []
        self.used_combinations = []
        self.generation_count = 0
        self.quality_score = 100
        self._cache = {}  # Кэш для ускорения генерации

    def _to_accusative_case(self, phrase: str) -> str:
        """
        Склоняет фразу в винительный падеж (для 'что' в шагах приготовления)
        """

        exceptions = {
            "Греческий йогурт": "греческого йогурта",
            "Цельнозерновой хлеб": "цельнозерновой хлеб",
            "Рис белый (варёный)": "белый варёный рис",
            "Рис бурый варёный": "бурый варёный рис",
            "Куриная грудка": "куриную грудку",
            "Филе индейки": "филе индейки",
            "Треска": "треску",
            "Морковь": "морковь",
            "Овсянка": "овсянку",
            "Творог обезжиренный": "обезжиренного творога",
            "Банан": "банан",
            "Яблоко": "яблоко",
            "Огурцы": "огурцы",
            "Брокколи": "брокколи",
            "Болгарский перец": "болгарский перец",
            "Гречка варёная": "варёную гречку",
            "Яйца": "яйца",
            "Лосось": "лосося",
            "Тунец консервированный": "консервированного тунца",
            "Креветки": "креветки",
            "Тофу": "тофу",
            "Протеиновый порошок": "протеинового порошка",
            "Кускус": "кускус",
            "Чечевица": "чечевицу",
            "Нут": "нут",
            "Фасоль": "фасоль",
            "Киноа": "киноа",
            "Цветная капуста": "цветную капусту",
            "Баклажан": "баклажан",
            "Стручковая фасоль": "стручковую фасоль",
            "Тыква": "тыкву",
            "Шпинат": "шпинат",
            "Киви": "киви",
            "Манго": "манго",
            "Грейпфрут": "грейпфрут",
            "Ананас": "ананас",
            "Ягоды": "ягоды",
            "Авокадо": "авокадо",
            "Миндаль": "миндаль",
            "Грецкие орехи": "грецкие орехи",
            "Семена чиа": "семена чиа",
            "Льняное семя": "льняное семя",
            "Кешью": "кешью",
            "Фундук": "фундук",
            "Арахисовая паста": "арахисовой пасты",
            "Оливковое масло": "оливкового масла"
        }

        if phrase in exceptions:
            return exceptions[phrase]

        # Базовые правила для винительного падежа
        words = phrase.split()

        if len(words) >= 2:
            adj = words[0]
            noun = ' '.join(words[1:])

            # Склоняем прилагательное
            if adj.endswith('ый'):
                adj = adj[:-2] + 'ый'  # не меняется для муж. рода неодуш.
            elif adj.endswith('ой'):
                adj = adj[:-2] + 'ой'
            elif adj.endswith('ий'):
                adj = adj[:-2] + 'ий'
            elif adj.endswith('ая'):
                adj = adj[:-2] + 'ую'
            elif adj.endswith('яя'):
                adj = adj[:-2] + 'юю'

            # Склоняем существительное
            if noun.endswith('а'):
                noun = noun[:-1] + 'у'
            elif noun.endswith('я'):
                noun = noun[:-1] + 'ю'
            elif noun.endswith('ка'):
                noun = noun[:-1] + 'у'
            # Остальные не меняются

            return f"{adj.lower()} {noun}"
        else:
            word = phrase

            # Одно слово
            if word.endswith('а'):
                return word[:-1] + 'у'
            elif word.endswith('я'):
                return word[:-1] + 'ю'
            elif word.endswith('ка'):
                return word[:-1] + 'у'
            else:
                return word.lower()

    def _to_instrumental_case(self, phrase: str) -> str:
        """
        Склоняет фразу в творительный падеж (для 'с чем')
        Работает с простыми правилами русского языка
        """

        # Словарь исключений для сложных случаев
        exceptions = {
            "Греческий йогурт": "греческим йогуртом",
            "Цельнозерновой хлеб": "цельнозерновым хлебом",
            "Рис белый (варёный)": "белым варёным рисом",
            "Рис бурый варёный": "бурым варёным рисом",
            "Куриная грудка": "куриной грудкой",
            "Филе индейки": "филе индейки",
            "Треска": "треской",
            "Морковь": "морковью",
            "Овсянка": "овсянкой",
            "Творог обезжиренный": "обезжиренным творогом",
            "Банан": "бананом",
            "Яблоко": "яблоком",
            "Огурцы": "огурцами",
            "Брокколи": "брокколи",
            "Болгарский перец": "болгарским перцем",
            "Гречка варёная": "варёной гречкой",
            "Яйца": "яйцами",
            "Лосось": "лососем",
            "Тунец консервированный": "консервированным тунцом",
            "Креветки": "креветками",
            "Тофу": "тофу",
            "Протеиновый порошок": "протеиновым порошком",
            "Кускус": "кускусом",
            "Чечевица": "чечевицей",
            "Нут": "нутом",
            "Фасоль": "фасолью",
            "Киноа": "киноа",
            "Цветная капуста": "цветной капустой",
            "Баклажан": "баклажаном",
            "Стручковая фасоль": "стручковой фасолью",
            "Тыква": "тыквой",
            "Шпинат": "шпинатом",
            "Киви": "киви",
            "Манго": "манго",
            "Грейпфрут": "грейпфрутом",
            "Ананас": "ананасом",
            "Ягоды": "ягодами",
            "Авокадо": "авокадо",
            "Миндаль": "миндалём",
            "Грецкие орехи": "грецкими орехами",
            "Семена чиа": "семенами чиа",
            "Льняное семя": "льняным семенем",
            "Кешью": "кешью",
            "Фундук": "фундуком",
            "Арахисовая паста": "арахисовой пастой",
            "Оливковое масло": "оливковым маслом"
        }

        # Проверяем словарь исключений
        if phrase in exceptions:
            return exceptions[phrase]

        # Базовые правила склонения
        words = phrase.split()

        if len(words) >= 2:
            # Склоняем прилагательное и существительное
            adj = words[0]
            noun = ' '.join(words[1:])

            # Склоняем прилагательное
            if adj.endswith('ый'):
                adj = adj[:-2] + 'ым'
            elif adj.endswith('ой'):
                adj = adj[:-2] + 'ым'
            elif adj.endswith('ий'):
                adj = adj[:-2] + 'им'
            elif adj.endswith('ая'):
                adj = adj[:-2] + 'ой'
            elif adj.endswith('яя'):
                adj = adj[:-2] + 'ей'

            # Склоняем существительное
            if noun.endswith('а'):
                noun = noun[:-1] + 'ой'
            elif noun.endswith('я'):
                noun = noun[:-1] + 'ей'
            elif noun.endswith('ь'):
                noun = noun[:-1] + 'ью'
            elif noun.endswith('ка'):
                noun = noun[:-1] + 'ой'
            else:
                # Мужской род на согласную
                noun = noun + 'ом'

            return f"{adj.lower()} {noun}"
        else:
            # Одно слово
            word = phrase

            if word.endswith('а'):
                return word[:-1] + 'ой'
            elif word.endswith('я'):
                return word[:-1] + 'ей'
            elif word.endswith('ь'):
                return word[:-1] + 'ью'
            elif word.endswith('ка'):
                return word[:-1] + 'ой'
            else:
                return word + 'ом'

    def generate_meal_plan(self, profile: dict, preferences: dict, language: str = "ru") -> str:
        """
        Генерирует идеальный план питания с защитой от ошибок

        Args:
            profile: {age, weight, height, gender, goal, activity_level}
            preferences: {available_products, exclude, allergies, favorites, cooking_time}
            language: ru/en/uz

        Returns:
            Полный план питания в виде форматированного текста
        """

        # Валидация входных данных
        if not profile or not isinstance(profile, dict):
            profile = {}
        if not preferences or not isinstance(preferences, dict):
            preferences = {}

        # ШАГ 1: Расчёт метаболизма
        try:
            metabolism = self._calculate_metabolism(profile)
        except Exception:
            metabolism = {'bmr': 1500, 'tdee': 2000, 'target_calories': 2000}

        # ШАГ 2: Распределение калорий по приёмам пищи
        # Проверяем, нужны ли перекусы (по умолчанию НЕТ)
        include_snacks = preferences.get('include_snacks', False)
        if include_snacks:
            meal_structure = 'breakfast,snack,lunch,snack,dinner'
        else:
            meal_structure = 'breakfast,lunch,dinner'

        meal_distribution = self._distribute_calories(
            total_calories=metabolism['target_calories'],
            meal_structure=meal_structure
        )

        # ШАГ 3: Подбор продуктов на основе предпочтений
        available_products = self._filter_products(preferences)

        # ШАГ 4: Генерация каждого приёма пищи
        meals = []
        for meal_type, calories in meal_distribution.items():
            meal = self._generate_meal(
                meal_type=meal_type,
                target_calories=calories,
                available_products=available_products,
                preferences=preferences,
                language=language,
                goal=profile.get('goal', 'maintain')  # ПЕРЕДАЁМ ЦЕЛЬ ПОЛЬЗОВАТЕЛЯ
            )
            meals.append(meal)

        # ШАГ 5: Проверка и корректировка
        meals = self._adjust_to_target(meals, metabolism['target_calories'])

        # ШАГ 6: Форматирование вывода
        formatted_plan = self._format_plan(
            meals=meals,
            metabolism=metabolism,
            language=language
        )

        # Увеличиваем счётчик генераций
        self.generation_count += 1

        # Оценка разнообразия
        unique_products = len(set(self.used_products_history[-15:]))
        diversity_score = min(100, unique_products * 7)

        # Запоминаем успешные комбинации продуктов
        meal_combinations = []
        for meal in meals:
            products_in_meal = list(meal.get('ingredients', {}).keys())
            if len(products_in_meal) >= 2:
                combo = tuple(sorted(products_in_meal[:3]))  # Топ-3 продукта
                meal_combinations.append(combo)
        self.used_combinations.extend(meal_combinations)

        # Очистка старых данных
        if len(self.used_combinations) > 50:
            self.used_combinations = self.used_combinations[-30:]
        if len(self.used_products_history) > 30:
            self.used_products_history = self.used_products_history[-20:]

        # ШАГ 7: AI-перевод на выбранный язык
        if language != "ru":
            formatted_plan = translate_with_ai(formatted_plan, language)

        return formatted_plan

    def _calculate_metabolism(self, profile: dict) -> dict:
        """Расчёт BMR, TDEE, целевых калорий и водного баланса"""

        weight = profile.get('weight', 70)
        height = profile.get('height', 170)
        age = profile.get('age', 25)
        gender = profile.get('gender', 'male')

        if gender in ['male', 'мужской', 'erkak']:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        activity_multipliers = {
            'beginner': 1.375,
            'intermediate': 1.55,
            'advanced': 1.725,
            'athlete': 1.9
        }

        activity_level = profile.get('activity_level', 'intermediate')
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)

        goal = profile.get('goal', 'maintain')
        if goal in ['lose_weight', 'похудение', 'vazn_yo\'qotish']:
            target_calories = tdee * 0.90  # Мягкий дефицит 10% (было 15%)
        elif goal in ['gain_muscle', 'набор_массы', 'massa_oshirish']:
            target_calories = tdee * 1.15
        else:
            target_calories = tdee

        # Расчёт водного баланса (35мл на кг веса)
        water_ml = round(weight * 35)

        return {
            'bmr': round(bmr),
            'tdee': round(tdee),
            'target_calories': round(target_calories),
            'water_ml': water_ml,
            'goal': goal
        }

    def _distribute_calories(self, total_calories: int, meal_structure: str) -> dict:
        """Распределяет калории по приёмам пищи"""

        if meal_structure == 'breakfast,lunch,dinner':
            return {
                'breakfast': round(total_calories * 0.25),
                'lunch': round(total_calories * 0.40),
                'dinner': round(total_calories * 0.35)
            }
        elif meal_structure == 'breakfast,snack,lunch,snack,dinner':
            return {
                'breakfast': round(total_calories * 0.20),
                'snack1': round(total_calories * 0.10),
                'lunch': round(total_calories * 0.35),
                'snack2': round(total_calories * 0.10),
                'dinner': round(total_calories * 0.25)
            }
        else:
            # Равномерное распределение
            meals_count = meal_structure.count(',') + 1
            per_meal = round(total_calories / meals_count)
            return {f'meal_{i}': per_meal for i in range(meals_count)}

    def _filter_products(self, preferences: dict) -> list:
        """Фильтрует продукты по предпочтениям"""

        available = NutritionDatabase.get_all_products()

        # Исключаем аллергены
        allergies = preferences.get('allergies', [])
        if isinstance(allergies, str):
            allergies = [allergies] if allergies else []
        if allergies:
            available = [p for p in available if p['key'] not in allergies]

        # Исключаем нежелательные продукты
        exclude = preferences.get('exclude', [])
        if isinstance(exclude, str):
            exclude = [exclude] if exclude else []
        if exclude:
            available = [p for p in available if p['key'] not in exclude]

        return available

    def _generate_meal(self, meal_type: str, target_calories: int,
                      available_products: list, preferences: dict, language: str, goal: str = 'maintain') -> dict:
        """
        Генерирует один приём пищи из ГОТОВЫХ РЕЦЕПТОВ
        Использует базу MEGA_RECIPES (636 рецептов)
        Фильтрует по доступным продуктам пользователя
        """

        # Пытаемся найти готовый рецепт из базы
        recipe = self._find_suitable_recipe(
            meal_type=meal_type,
            target_calories=target_calories,
            available_products=available_products,
            preferences=preferences,
            language=language,
            goal=goal
        )

        if recipe:
            return recipe

        # Если не нашли готовый рецепт, генерируем из продуктов (старая логика как запасная)
        return self._generate_meal_from_products(
            meal_type=meal_type,
            target_calories=target_calories,
            available_products=available_products,
            preferences=preferences,
            language=language,
            goal=goal
        )

    def _find_suitable_recipe(self, meal_type: str, target_calories: int,
                             available_products: list, preferences: dict, language: str, goal: str = 'maintain') -> dict:
        """
        Находит подходящий ГОТОВЫЙ РЕЦЕПТ из базы MEGA_RECIPES
        Фильтрует по:
        - Типу приёма пищи (breakfast/lunch/dinner/snack)
        - Доступным продуктам пользователя (по названиям ингредиентов)
        - Целевым калориям (±30%)
        """

        # Получаем все рецепты нужного типа с учетом цели
        all_recipes = self.recipe_db.search_by_meal_type(meal_type, goal)

        if not all_recipes:
            return None

        # Парсим доступные продукты от пользователя
        user_input_products = preferences.get('available_products', '')
        excluded = set(preferences.get('exclude', []))

        # Фильтруем рецепты
        suitable = []
        for recipe_data in all_recipes:
            recipe_ingredients = recipe_data.get('ingredients', {}).keys()

            # Проверяем калории (±30% от цели)
            recipe_calories = recipe_data.get('calories', 0)
            calories_ok = target_calories * 0.7 <= recipe_calories <= target_calories * 1.3

            if not calories_ok:
                continue

            # Проверяем исключения
            has_excluded = any(excl in str(recipe_ingredients).lower() for excl in excluded if excl)
            if has_excluded:
                continue

            # Если пользователь указал продукты - проверяем совпадения
            if user_input_products and user_input_products.strip() and user_input_products not in ['-', 'нет', 'все']:
                # Разбиваем ввод пользователя на отдельные продукты
                # Удаляем союзы и предлоги
                ignore_words = ['и', 'с', 'или', 'на', 'в', 'из', 'от', 'для', 'по', 'к', 'у',
                               'and', 'with', 'or', 'on', 'in', 'from', 'for', 'to', 'at']
                user_products_list = [p.strip().lower() for p in user_input_products.replace(',', ' ').split()
                                     if p.strip() and p.strip().lower() not in ignore_words]

                # Проверяем, содержит ли рецепт хотя бы один из продуктов пользователя
                recipe_ingredients_str = ' '.join(recipe_ingredients).lower()
                match_count = sum(1 for user_prod in user_products_list
                                 if any(user_prod in ing.lower() for ing in recipe_ingredients))

                # Если нашлось хотя бы одно совпадение - рецепт подходит
                if match_count > 0:
                    suitable.append((recipe_data, match_count))
            else:
                # Если продукты не указаны - берем любой рецепт
                suitable.append((recipe_data, 0))

        if not suitable:
            return None

        # Сортируем по количеству совпадений (больше совпадений = лучше)
        suitable.sort(key=lambda x: x[1], reverse=True)

        # Берем топ-3 лучших совпадения и выбираем случайный из них
        top_recipes = suitable[:min(3, len(suitable))]
        chosen_recipe, _ = random.choice(top_recipes)

        # Конвертируем рецепт в нужный формат
        return self._convert_recipe_to_meal(chosen_recipe, language)

    def _convert_recipe_to_meal(self, recipe: dict, language: str) -> dict:
        """Конвертирует рецепт из MEGA_RECIPES в формат meal"""

        # Получаем название на нужном языке
        name = recipe.get(f'name_{language}', recipe.get('name_ru', 'Блюдо'))

        # Формируем ингредиенты с полными данными
        ingredients = {}
        for ing_key, grams in recipe.get('ingredients', {}).items():
            product_data = self.nutrition_db.get_product(ing_key)
            if product_data:
                ingredients[ing_key] = {
                    'grams': grams,
                    'name': product_data
                }

        # Получаем шаги приготовления (если есть в рецепте)
        steps_key = f'steps_{language}'
        steps = recipe.get(steps_key, recipe.get('steps_ru', []))

        # Если шагов нет, генерируем на основе cooking_level
        if not steps:
            steps = self._generate_steps_for_recipe(recipe, ingredients, language)

        # Получаем совет (если есть в рецепте)
        tip_key = f'tips_{language}'
        tip = recipe.get(tip_key, recipe.get('tips_ru', ''))

        # Если совета нет, генерируем
        if not tip:
            tip = self._generate_tip_for_recipe(recipe, language)

        return {
            'name': name,
            'ingredients': ingredients,
            'steps': steps,
            'nutrition': {
                'calories': recipe.get('calories', 0),
                'protein': recipe.get('protein', 0),
                'fat': recipe.get('fat', 0),
                'carbs': recipe.get('carbs', 0)
            },
            'tip': tip,
            'meal_type': recipe.get('meal_type', 'breakfast'),
            'cooking_time': recipe.get('cooking_time_minutes', 30),
            'difficulty': recipe.get('difficulty', 'medium')
        }

    def _generate_steps_for_recipe(self, recipe: dict, ingredients: dict, language: str) -> list:
        """Генерирует шаги приготовления для рецепта на основе cooking_level"""
        cooking_level = recipe.get('cooking_level', 'full_cook')
        name = recipe.get('name_ru', '')

        templates = {
            'ru': {
                'no_cook': [
                    "Подготовьте ингредиенты",
                    "Подавайте сразу"
                ],
                'minimal_cook': [
                    "Подготовьте ингредиенты",
                    "Приготовьте блюдо согласно рецепту",
                    "Подавайте в горячем виде"
                ],
                'full_cook': [
                    "Подготовьте все ингредиенты",
                    "Приготовьте основные компоненты блюда",
                    "Смешайте ингредиенты и доведите до готовности",
                    "Подавайте горячим"
                ]
            },
            'en': {
                'no_cook': [
                    "Prepare ingredients",
                    "Serve immediately"
                ],
                'minimal_cook': [
                    "Prepare ingredients",
                    "Cook according to recipe",
                    "Serve hot"
                ],
                'full_cook': [
                    "Prepare all ingredients",
                    "Cook main components",
                    "Mix ingredients and finish cooking",
                    "Serve hot"
                ]
            },
            'uz': {
                'no_cook': [
                    "Ingredientlarni tayyorlang",
                    "Darhol xizmat qiling"
                ],
                'minimal_cook': [
                    "Ingredientlarni tayyorlang",
                    "Retsept bo'yicha pishiring",
                    "Issiq holda xizmat qiling"
                ],
                'full_cook': [
                    "Barcha ingredientlarni tayyorlang",
                    "Asosiy komponentlarni pishiring",
                    "Ingredientlarni aralashtiring va pishirishni yakunlang",
                    "Issiq holda xizmat qiling"
                ]
            }
        }

        return templates.get(language, templates['ru']).get(cooking_level, templates[language]['minimal_cook'])

    def _generate_tip_for_recipe(self, recipe: dict, language: str) -> str:
        """Генерирует полезный совет для рецепта"""
        meal_type = recipe.get('meal_type', '')
        calories = recipe.get('calories', 0)
        protein = recipe.get('protein', 0)

        tips = {
            'ru': {
                'high_protein': "Белок надолго утоляет голод и помогает в восстановлении мышц после тренировок.",
                'low_calorie': "Низкокалорийное блюдо идеально подходит для снижения веса.",
                'breakfast': "Сбалансированный завтрак даёт энергию на весь день.",
                'lunch': "Полноценный обед - основа здорового питания.",
                'dinner': "Легкий ужин способствует качественному сну и восстановлению.",
                'snack': "Полезный перекус помогает контролировать аппетит.",
                'high_energy': "Отличный выбор для активного образа жизни.",
                'balanced': "Сбалансированное блюдо содержит все необходимые макронутриенты."
            },
            'en': {
                'high_protein': "Protein keeps you full and helps muscle recovery after workouts.",
                'low_calorie': "Low-calorie dish perfect for weight loss.",
                'breakfast': "Balanced breakfast provides energy for the whole day.",
                'lunch': "Full lunch - foundation of healthy eating.",
                'dinner': "Light dinner promotes quality sleep and recovery.",
                'snack': "Healthy snack helps control appetite.",
                'high_energy': "Great choice for active lifestyle.",
                'balanced': "Balanced dish contains all necessary macronutrients."
            },
            'uz': {
                'high_protein': "Protein ochlikni uzoq vaqt qondiradi va mushaklar tiklanishiga yordam beradi.",
                'low_calorie': "Kam kaloriyali taom vazn yo'qotish uchun ideal.",
                'breakfast': "Muvozanatli nonushta kun bo'yi energiya beradi.",
                'lunch': "To'liq tushlik - sog'lom ovqatlanish asosi.",
                'dinner': "Yengil kechki ovqat sifatli uyqu va tiklanishga yordam beradi.",
                'snack': "Foydali gazak ishtahani nazorat qilishga yordam beradi.",
                'high_energy': "Faol turmush tarzi uchun ajoyib tanlov.",
                'balanced': "Muvozanatli taom barcha zarur makronutrientlarni o'z ichiga oladi."
            }
        }

        lang_tips = tips.get(language, tips['ru'])

        # Выбираем совет на основе характеристик блюда
        if protein > 25:
            return lang_tips['high_protein']
        elif calories < 250:
            return lang_tips['low_calorie']
        elif meal_type == 'breakfast':
            return lang_tips['breakfast']
        elif meal_type == 'lunch':
            return lang_tips['lunch']
        elif meal_type == 'dinner':
            return lang_tips['dinner']
        elif 'snack' in meal_type:
            return lang_tips['snack']
        elif calories > 500:
            return lang_tips['high_energy']
        else:
            return lang_tips['balanced']

    def _generate_meal_from_products(self, meal_type: str, target_calories: int,
                      available_products: list, preferences: dict, language: str, goal: str = 'maintain') -> dict:
        """
        СТАРАЯ ЛОГИКА - генерирует блюдо из отдельных продуктов
        Используется только если не найден готовый рецепт
        """

        # Определяем макросы для приёма пищи
        macros = self._calculate_meal_macros(target_calories, meal_type)

        # Подбираем продукты (ПЕРЕДАЁМ ЦЕЛЬ!)
        selected_products = self._select_products_intelligent(
            available_products=available_products,
            target_calories=target_calories,
            target_macros=macros,
            meal_type=meal_type,
            preferences=preferences,
            goal=goal,
            language=language
        )

        # Рассчитываем точные порции
        portions = self._calculate_portions_precise(
            products=selected_products,
            target_calories=target_calories,
            target_macros=macros
        )

        # Генерируем шаги приготовления
        cooking_steps = self._generate_cooking_steps(
            portions=portions,
            language=language
        )

        # Генерируем полезный совет
        tip = self._generate_tip(portions, language)

        # Рассчитываем итоговую питательность
        total_nutrition = self._calculate_total_nutrition(portions)

        # Оценка времени и сложности
        cooking_time = sum(p.get('name', {}).get('cooking_time_minutes', 15) for p in portions.values()) // len(portions)
        difficulty = 'easy' if len(portions) <= 3 else 'medium' if len(portions) <= 5 else 'hard'

        return {
            'name': self._generate_dish_name(portions, meal_type, language),
            'ingredients': portions,
            'steps': cooking_steps,
            'nutrition': total_nutrition,
            'tip': tip,
            'meal_type': meal_type,
            'cooking_time': cooking_time,
            'difficulty': difficulty
        }

    def _calculate_meal_macros(self, target_calories: int, meal_type: str) -> dict:
        """Рассчитывает целевые макросы для приёма пищи"""

        # Стандартное распределение: 30% белки, 25% жиры, 45% углеводы
        protein_calories = target_calories * 0.30
        fat_calories = target_calories * 0.25
        carbs_calories = target_calories * 0.45

        # Конвертация калорий в граммы (1г белка = 4 ккал, 1г жира = 9 ккал, 1г углеводов = 4 ккал)
        return {
            'protein': round(protein_calories / 4, 1),
            'fat': round(fat_calories / 9, 1),
            'carbs': round(carbs_calories / 4, 1)
        }

    def _select_products_intelligent(self, available_products: list,
                                    target_calories: int, target_macros: dict,
                                    meal_type: str, preferences: dict, goal: str = 'maintain', language: str = 'ru') -> list:
        """
        ИНТЕЛЛЕКТУАЛЬНЫЙ подбор продуктов с РАЗНООБРАЗИЕМ и УЧЁТОМ ЦЕЛИ
        Учитывает: тип приёма пищи, предпочтения, макросы, калории, историю выбора, ЦЕЛЬ ПОЛЬЗОВАТЕЛЯ
        """

        selected = []

        # Фильтруем продукты, которые уже использовались
        fresh_products = [p for p in available_products
                         if p['key'] not in self.used_products_history[-10:]]  # Последние 10

        # Если слишком много отфильтровали, берем все
        if len(fresh_products) < 5:
            fresh_products = available_products

        # Для завтрака - энергия на весь день
        if meal_type == 'breakfast':
            # УГЛЕВОДНАЯ БАЗА для энергии
            breakfast_carbs = {
                'en': ['oatmeal', 'whole_grain_bread', 'buckwheat'],
                'uz': ['jo\'xori_uni', 'non', 'guruch', 'grechka'],
                'ru': ['овсянка', 'хлеб_цельнозерновой', 'гречка']
            }
            carb_products = [p for p in fresh_products
                           if p['category'] == 'carbs' and p['key'] in breakfast_carbs.get(language, breakfast_carbs['ru'])]
            if not carb_products:
                carb_products = [p for p in fresh_products if p['category'] == 'carbs']
            if carb_products:
                base = self._choose_best_product(carb_products, preferences, priority='energy', goal=goal)
                selected.append(base)
                self.used_products_history.append(base['key'])

            # БЕЛОК - яйца, творог, йогурт (подходит для завтрака)
            if language == 'en':
                breakfast_proteins = ['eggs', 'cottage_cheese', 'greek_yogurt', 'protein_powder']
            elif language == 'uz':
                breakfast_proteins = ['tuxum', 'tvorog', 'yogurt', 'protein_kukun']
            else:  # ru
                breakfast_proteins = ['яйца', 'творог', 'греческий_йогурт', 'протеин_порошок']
            protein_products = [p for p in fresh_products
                              if p['category'] in ['protein', 'dairy']
                              and (p['key'] in breakfast_proteins or p['cooking_time_minutes'] <= 5)]
            if protein_products:
                protein = self._choose_best_product(protein_products, preferences, priority='quick_cook', goal=goal)
                selected.append(protein)
                self.used_products_history.append(protein['key'])

            # ФРУКТЫ - обязательно на завтрак
            fruit_products = [p for p in fresh_products if p['category'] == 'fruits']
            if fruit_products:
                fruit = self._choose_best_product(fruit_products, preferences, goal=goal)
                selected.append(fruit)
                self.used_products_history.append(fruit['key'])

            # Иногда добавляем орехи/семена
            if random.random() > 0.5:
                nuts = [p for p in fresh_products if p['category'] == 'nuts']
                if nuts:
                    nut = self._choose_best_product(nuts, preferences, goal=goal)
                    selected.append(nut)
                    self.used_products_history.append(nut['key'])

        # Для обеда - полноценное блюдо: мясо/рыба + гарнир + овощи
        elif meal_type == 'lunch':
            # БЕЛКОВАЯ ОСНОВА - мясо или рыба (НЕ яйца, НЕ творог)
            if language == 'en':
                meat_fish = ['chicken_breast', 'beef', 'cod', 'salmon', 'turkey', 'tuna', 'shrimp']
            elif language == 'uz':
                meat_fish = ['tovuq_ko\'kragi', 'mol_go\'shti', 'baliq', 'losos', 'kurka', 'tunets', 'krevetka']
            else:  # ru
                meat_fish = ['куриная_грудка', 'говядина', 'рыба_треска', 'лосось', 'индейка', 'тунец', 'креветки']
            protein_products = [p for p in fresh_products
                              if p['category'] == 'protein' and p['key'] in meat_fish]
            if protein_products:
                main_protein = self._choose_best_product(protein_products, preferences, priority='satiety', goal=goal)
                selected.append(main_protein)
                self.used_products_history.append(main_protein['key'])

            # УГЛЕВОДНЫЙ ГАРНИР - рис, гречка, макароны, картофель
            if language == 'en':
                side_carbs = ['white_rice', 'brown_rice', 'buckwheat', 'pasta', 'potato', 'sweet_potato', 'couscous', 'lentils', 'chickpeas', 'beans']
            elif language == 'uz':
                side_carbs = ['oq_guruch', 'jigarrang_guruch', 'grechka', 'makaron', 'kartoshka', 'shirin_kartoshka', 'kuskus', 'yasmiq', 'noxat', 'loviya']
            else:  # ru
                side_carbs = ['рис_белый', 'рис_бурый', 'гречка', 'макароны', 'картофель', 'батат', 'кускус', 'чечевица', 'нут', 'фасоль']
            carb_products = [p for p in fresh_products
                           if p['category'] == 'carbs' and p['key'] in side_carbs]
            if carb_products:
                garnish = self._choose_best_product(carb_products, preferences, goal=goal)
                selected.append(garnish)
                self.used_products_history.append(garnish['key'])

            # ОВОЩИ - разнообразные
            veggie_products = [p for p in fresh_products if p['category'] == 'vegetables']
            if veggie_products:
                veggies = self._choose_best_product(veggie_products, preferences, goal=goal)
                selected.append(veggies)
                self.used_products_history.append(veggies['key'])

        # Для ужина - легкий белок + овощи (меньше углеводов)
        elif meal_type == 'dinner':
            # ЛЕГКИЙ БЕЛОК - рыба, курица, морепродукты
            if language == 'en':
                light_proteins = ['cod', 'salmon', 'chicken_breast', 'turkey', 'shrimp', 'tuna', 'tofu']
            elif language == 'uz':
                light_proteins = ['baliq', 'losos', 'tovuq_ko\'kragi', 'kurka', 'krevetka', 'tunets', 'tofu']
            else:  # ru
                light_proteins = ['рыба_треска', 'лосось', 'куриная_грудка', 'индейка', 'креветки', 'тунец', 'тофу']
            protein_products = [p for p in fresh_products
                              if p['category'] == 'protein' and p['key'] in light_proteins]
            if protein_products:
                protein = self._choose_best_product(protein_products, preferences, priority='light', goal=goal)
                selected.append(protein)
                self.used_products_history.append(protein['key'])

            # ОВОЩИ - 2-3 вида
            veggie_products = [p for p in fresh_products if p['category'] == 'vegetables']
            for i in range(min(2, len(veggie_products))):
                if veggie_products:
                    veggie = self._choose_best_product(veggie_products, preferences)
                    selected.append(veggie)
                    self.used_products_history.append(veggie['key'])
                    # Удаляем выбранный продукт из списка
                    veggie_products = [v for v in veggie_products if v['key'] != veggie['key']]

            # Иногда добавляем легкие углеводы
            if target_calories > 400:
                light_carbs = ['батат', 'чечевица']
                carb_products = [p for p in fresh_products
                               if p['category'] == 'carbs' and p['key'] in light_carbs]
                if carb_products and random.random() > 0.6:
                    carb = self._choose_best_product(carb_products, preferences)
                    selected.append(carb)
                    self.used_products_history.append(carb['key'])

        # Для перекусов - легкие продукты для быстрого перекуса
        elif meal_type in ['snack', 'snack1', 'snack2']:
            # ФРУКТЫ - идеально для перекуса
            fruit_products = [p for p in fresh_products if p['category'] == 'fruits']
            if fruit_products and random.random() > 0.3:
                fruit = self._choose_best_product(fruit_products, preferences, goal=goal)
                selected.append(fruit)
                self.used_products_history.append(fruit['key'])

            # ОРЕХИ или СЕМЕНА - энергия и полезные жиры
            nuts = [p for p in fresh_products if p['category'] == 'nuts']
            if nuts and random.random() > 0.4:
                nut = self._choose_best_product(nuts, preferences, goal=goal)
                selected.append(nut)
                self.used_products_history.append(nut['key'])

            # МОЛОЧНЫЕ - йогурт, творог, сыр
            if language == 'en':
                snack_dairy = ['greek_yogurt', 'cottage_cheese', 'cheese', 'kefir']
            elif language == 'uz':
                snack_dairy = ['yogurt', 'tvorog', 'pishloq', 'kefir']
            else:  # ru
                snack_dairy = ['греческий_йогурт', 'творог', 'сыр', 'кефир']
            dairy_products = [p for p in fresh_products
                            if p['category'] == 'dairy' and p['key'] in snack_dairy]
            if dairy_products and random.random() > 0.5:
                dairy = self._choose_best_product(dairy_products, preferences, priority='quick_cook', goal=goal)
                selected.append(dairy)
                self.used_products_history.append(dairy['key'])

        # Если не удалось подобрать - берем случайные
        if not selected:
            selected = random.sample(fresh_products, min(3, len(fresh_products)))
            for p in selected:
                self.used_products_history.append(p['key'])

        return selected

    def _choose_best_product(self, products: list, preferences: dict, priority: str = None, goal: str = None) -> dict:
        """
        Выбирает лучший продукт из списка на основе приоритетов И ЦЕЛЕЙ ПОЛЬЗОВАТЕЛЯ

        Новое: учитываем цель (gain_muscle, lose_weight, maintain) для более точного подбора
        """

        if not products:
            return None

        # Проверяем любимые продукты
        favorites = preferences.get('favorites', [])
        if isinstance(favorites, str):
            # Разбиваем строку на отдельные слова
            favorites = [f.strip() for f in favorites.replace(',', ' ').replace(';', ' ').split() if f.strip()]
        if favorites:
            # Точные совпадения
            for product in products:
                if product['key'] in favorites:
                    return product
            # Частичные совпадения: "курица" → "куриная_грудка", "рис" → "рис_белый"
            for fav in favorites:
                fav_lower = fav.lower()
                if len(fav_lower) < 3 or fav_lower in ['and', 'или', 'with', 'с', 'the']:
                    continue
                for product in products:
                    key_lower = product['key'].lower()
                    if fav_lower in key_lower or key_lower.startswith(fav_lower):
                        return product

        # УМНЫЙ ВЫБОР ПОД ЦЕЛЬ ПОЛЬЗОВАТЕЛЯ
        if goal == 'gain_muscle':
            # Для набора массы - приоритет на высококалорийные и белковые продукты
            if priority == 'energy':
                # Предпочитаем сложные углеводы с высокой калорийностью
                return max(products, key=lambda p: p['calories_per_100g'] + p['carbs_per_100g'] * 2)
            elif priority == 'satiety':
                # Максимизируем белок
                return max(products, key=lambda p: p['protein_per_100g'])
            else:
                # По умолчанию - белок + калории
                return max(products, key=lambda p: p['protein_per_100g'] * 2 + p['calories_per_100g'] * 0.5)

        elif goal == 'lose_weight':
            # Для похудения - приоритет на низкокалорийные и объемные продукты
            if priority == 'energy':
                # Углеводы с низким гликемическим индексом (бурый рис, гречка)
                low_gi = ['рис_бурый', 'гречка', 'овсянка', 'батат']
                low_gi_products = [p for p in products if p['key'] in low_gi]
                if low_gi_products:
                    return min(low_gi_products, key=lambda p: p['calories_per_100g'])
                return min(products, key=lambda p: p['calories_per_100g'])
            elif priority == 'satiety':
                # Белок с минимальными калориями (куриная грудка, треска)
                lean_proteins = ['куриная_грудка', 'индейка', 'рыба_треска', 'креветки', 'творог']
                lean = [p for p in products if p['key'] in lean_proteins]
                if lean:
                    return max(lean, key=lambda p: p['protein_per_100g'] / max(p['fat_per_100g'], 1))
                return max(products, key=lambda p: p['protein_per_100g'] - p['fat_per_100g'])
            elif priority == 'light':
                # Минимум калорий, максимум объема
                return min(products, key=lambda p: p['calories_per_100g'])
            else:
                # По умолчанию - низкокалорийные с высоким белком
                return min(products, key=lambda p: p['calories_per_100g'] - p['protein_per_100g'] * 2)

        elif goal == 'maintain':
            # Для поддержания - сбалансированный подход
            if priority == 'energy':
                # Средние по калорийности углеводы
                return sorted(products, key=lambda p: abs(p['calories_per_100g'] - 150))[0]
            elif priority == 'satiety':
                # Сбалансированный белок
                return max(products, key=lambda p: p['protein_per_100g'])
            else:
                # Баланс всех макросов
                return max(products, key=lambda p: (p['protein_per_100g'] + p['carbs_per_100g'] + p['fat_per_100g']) / 3)

        # КЛАССИЧЕСКИЕ ПРИОРИТЕТЫ (если цель не указана)
        if priority == 'energy':
            # Для энергии - высокие углеводы
            return max(products, key=lambda p: p['carbs_per_100g'])
        elif priority == 'satiety':
            # Для сытости - высокий белок
            return max(products, key=lambda p: p['protein_per_100g'])
        elif priority == 'light':
            # Для лёгкости - низкие калории
            return min(products, key=lambda p: p['calories_per_100g'])
        elif priority == 'quick_cook':
            # Для скорости - минимальное время готовки
            return min(products, key=lambda p: p['cooking_time_minutes'])
        else:
            # По умолчанию - первый доступный
            return products[0]

    def _calculate_portions_precise(self, products: list, target_calories: int, target_macros: dict) -> dict:
        """
        ТОЧНЫЙ расчёт порций для достижения целевых калорий
        Использует математическую оптимизацию
        """

        portions = {}
        remaining_calories = target_calories
        remaining_protein = target_macros['protein']
        remaining_carbs = target_macros['carbs']
        remaining_fat = target_macros['fat']

        for i, product in enumerate(products):
            if not product:
                continue

            # Определяем приоритет для продукта
            if product['category'] == 'protein':
                # Белковый продукт - стремимся покрыть норму белка
                needed_protein_grams = max(remaining_protein, 10)
                if product['protein_per_100g'] > 0:
                    grams = (needed_protein_grams / product['protein_per_100g']) * 100
                else:
                    grams = 100
            elif product['category'] == 'carbs':
                # Углеводный продукт - стремимся покрыть норму углеводов
                needed_carbs_grams = max(remaining_carbs, 20)
                if product['carbs_per_100g'] > 0:
                    grams = (needed_carbs_grams / product['carbs_per_100g']) * 100
                else:
                    grams = 100
            else:
                # Остальные - равномерно распределяем оставшиеся калории
                products_left = len(products) - i
                if products_left > 0:
                    calories_per_product = max(remaining_calories / products_left, 50)
                else:
                    calories_per_product = 100
                if product['calories_per_100g'] > 0:
                    grams = (calories_per_product / product['calories_per_100g']) * 100
                else:
                    grams = 100

            # Ограничиваем разумными пределами
            grams = max(10, min(grams, 500))

            # Округляем до практичных значений
            grams = self._round_to_practical(grams, product)

            # Рассчитываем питательность порции
            nutrition = NutritionDatabase.calculate_nutrition(
                product_key=product['key'],
                grams=int(grams)
            )

            # Сохраняем порцию
            # Используем product напрямую, а не только name_ru
            portions[product['key']] = {
                'name': product,  # Сохраняем весь объект продукта
                'grams': int(grams),
                'calories': nutrition['calories'],
                'protein': nutrition['protein'],
                'fat': nutrition['fat'],
                'carbs': nutrition['carbs'],
                'product_key': product['key']
            }

            # Вычитаем из оставшихся
            remaining_calories -= nutrition['calories']
            remaining_protein -= nutrition['protein']
            remaining_carbs -= nutrition['carbs']
            remaining_fat -= nutrition['fat']

        # Финальная корректировка если нужно
        if abs(remaining_calories) > 100 and portions:
            portions = self._fine_tune_portions(portions, target_calories)

        return portions

    def _round_to_practical(self, grams: float, product: dict) -> int:
        """Округляет до практичных кулинарных значений"""

        if 'яйц' in product['name_ru'].lower():
            # Яйца считаются штуками (1 яйцо ≈ 50г)
            eggs_count = max(1, round(grams / 50))
            return eggs_count * 50
        elif 'рис' in product['name_ru'].lower() or 'гречка' in product['name_ru'].lower():
            # Крупы в 25г шагами
            return max(25, round(grams / 25) * 25)
        elif product['category'] == 'protein':
            # Мясо/рыба в 50г шагами
            return max(50, round(grams / 50) * 50)
        elif product['category'] in ['nuts', 'sweeteners']:
            # Орехи и сладости в 5г шагами
            return max(5, round(grams / 5) * 5)
        else:
            # Остальное в 10г шагами
            return max(10, round(grams / 10) * 10)

    def _fine_tune_portions(self, portions: dict, target_calories: int) -> dict:
        """Финальная корректировка порций для точного попадания в калорийность"""

        current_calories = sum(p['calories'] for p in portions.values())
        diff = target_calories - current_calories

        if abs(diff) < 50:
            return portions

        # Находим продукт с максимальной калорийностью для корректировки
        max_cal_product = max(portions.items(), key=lambda x: x[1]['calories'])
        product_name = max_cal_product[0]
        product_data = max_cal_product[1]

        # Рассчитываем новый вес
        product_key = product_data['product_key']
        product_info = NutritionDatabase.get_product(product_key)

        if product_info and product_info['calories_per_100g'] > 0:
            new_calories = product_data['calories'] + diff
            new_grams = (new_calories / product_info['calories_per_100g']) * 100
            new_grams = max(10, int(new_grams))

            # Пересчитываем порцию
            new_nutrition = NutritionDatabase.calculate_nutrition(product_key, new_grams)
            portions[product_name] = {
                'grams': new_grams,
                'calories': new_nutrition['calories'],
                'protein': new_nutrition['protein'],
                'fat': new_nutrition['fat'],
                'carbs': new_nutrition['carbs'],
                'product_key': product_key
            }

        return portions

    def _generate_cooking_steps(self, portions: dict, language: str) -> list:
        """Генерирует шаги приготовления"""

        steps = []

        # Шаг 1: Подготовка
        prep_step = self._generate_prep_step(portions, language)
        if prep_step:
            steps.append(prep_step)

        # Шаг 2-N: Готовка
        cooking_steps = self._generate_cooking_sequence(portions, language)
        steps.extend(cooking_steps)

        # Последний шаг: Подача
        serving_step = self._generate_serving_step(language)
        if serving_step:
            steps.append(serving_step)

        return steps if steps else [self._get_default_step(language)]

    def _generate_prep_step(self, portions: dict, language: str) -> str:
        """Генерирует шаг подготовки с правильными названиями"""
        templates = {
            'ru': "Подготовьте все ингредиенты",
            'en': "Prepare all ingredients",
            'uz': "Barcha ingredientlarni tayyorlang"
        }
        return templates.get(language, templates['ru'])

    def _generate_cooking_sequence(self, portions: dict, language: str) -> list:
        """Генерирует последовательность готовки с деталями"""
        steps = []

        import random

        templates = {
            'ru': {
                'cook_meat': [
                    "Обжарьте {product} на среднем огне до золотистой корочки с обеих сторон ({grams}г)",
                    "Приготовьте {product} на сковороде-гриль 4-5 минут с каждой стороны ({grams}г)",
                    "Запекайте {product} в духовке при 180°C до готовности ({grams}г)",
                    "Тушите {product} на медленном огне под крышкой 15-20 минут ({grams}г)",
                    "Обжарьте {product} до румяной корочки, затем доведите до готовности в духовке ({grams}г)",
                ],
                'boil_grain': [
                    "Отварите {product} в подсоленной воде согласно инструкции на упаковке ({grams}г)",
                    "Промойте {product}, залейте водой в пропорции 1:2 и варите до готовности ({grams}г)",
                    "Доведите воду до кипения, добавьте {product} и варите на слабом огне до мягкости ({grams}г)",
                    "Залейте {product} кипятком, накройте крышкой и оставьте на 10-15 минут ({grams}г)",
                ],
                'steam_veg': [
                    "Приготовьте {product} на пару 5-7 минут до мягкости ({grams}г)",
                    "Отварите {product} в кипящей воде 3-4 минуты, затем слейте воду ({grams}г)",
                    "Обжарьте {product} на сковороде с небольшим количеством масла до мягкости ({grams}г)",
                    "Бланшируйте {product} в кипящей воде 2-3 минуты, затем охладите ({grams}г)",
                    "Запеките {product} в духовке при 200°C до золотистого цвета ({grams}г)",
                ],
                'raw': [
                    "Нарежьте {product} и добавьте в блюдо ({grams}г)",
                    "Добавьте {product} непосредственно перед подачей ({grams}г)",
                    "Мелко нарежьте {product} и смешайте с остальными ингредиентами ({grams}г)",
                ],
                'mix_dairy': [
                    "Смешайте {product} в миске до однородной консистенции ({grams}г)",
                    "Добавьте {product} и тщательно перемешайте ({grams}г)",
                ],
                'fry': [
                    "Обжарьте {product} на разогретой сковороде с маслом до румяности ({grams}г)",
                    "Приготовьте {product} на среднем огне, периодически помешивая ({grams}г)",
                ]
            },
            'en': {
                'cook_meat': [
                    "Cook {product} in a pan over medium heat until golden brown on both sides ({grams}g)",
                    "Grill {product} for 4-5 minutes on each side ({grams}g)",
                    "Bake {product} in the oven at 180°C until done ({grams}g)",
                ],
                'boil_grain': [
                    "Boil {product} in salted water according to package instructions ({grams}g)",
                    "Rinse {product}, add water in 1:2 ratio and cook until done ({grams}g)",
                ],
                'steam_veg': [
                    "Steam {product} for 5-7 minutes until tender ({grams}g)",
                    "Boil {product} in boiling water for 3-4 minutes, then drain ({grams}g)",
                ],
                'raw': [
                    "Chop {product} and add to the dish ({grams}g)",
                    "Add {product} just before serving ({grams}g)",
                ],
                'mix_dairy': [
                    "Mix {product} in a bowl until smooth ({grams}g)",
                ],
                'fry': [
                    "Fry {product} in a pan until golden ({grams}g)",
                ]
            },
            'uz': {
                'cook_meat': [
                    "{product}ni tovada yoki grilda pishiring ({grams}g)",
                ],
                'boil_grain': [
                    "{product}ni tayyor bo'lguncha qaynatib oling ({grams}g)",
                ],
                'steam_veg': [
                    "{product}ni bug'da yoki suvda pishiring ({grams}g)",
                ],
                'raw': [
                    "{product} qo'shing ({grams}g)",
                ],
                'mix_dairy': [
                    "{product}ni idishga soling ({grams}g)",
                ],
                'fry': [
                    "{product}ni tovada qovuring ({grams}g)",
                ]
            }
        }

        lang_templates = templates.get(language, templates['ru'])

        for product_key, data in portions.items():
            product_info = data.get('name')
            if not product_info:
                continue

            product_name = product_info.get(f'name_{language}', product_info.get('name_ru', ''))

            if language == 'ru':
                product_name_declined = self._to_accusative_case(product_name)
            else:
                product_name_declined = product_name.lower()

            # Определяем метод приготовления и выбираем случайный вариант
            if product_info['category'] == 'protein':
                if 'яйц' in product_info.get('name_ru', '').lower():
                    template = random.choice(lang_templates['fry'])
                elif 'raw' in product_info.get('cooking_methods', []):
                    template = random.choice(lang_templates['raw'])
                else:
                    template = random.choice(lang_templates['cook_meat'])
            elif product_info['category'] == 'carbs':
                if 'хлеб' in product_info.get('name_ru', '').lower():
                    template = random.choice(lang_templates['raw'])
                else:
                    template = random.choice(lang_templates['boil_grain'])
            elif product_info['category'] == 'vegetables':
                template = random.choice(lang_templates['steam_veg'])
            elif product_info['category'] in ['dairy', 'fruits', 'nuts', 'sweeteners', 'fats']:
                template = random.choice(lang_templates['raw'])
            else:
                template = random.choice(lang_templates['raw'])

            step = template.format(product=product_name_declined, grams=data['grams'])
            steps.append(step)

        return steps

    def _generate_serving_step(self, language: str) -> str:
        """Генерирует шаг подачи"""
        import random
        templates = {
            'ru': [
                "Красиво разложите на тарелке и подавайте теплым",
                "Украсьте зеленью и подавайте к столу",
                "Выложите на блюдо и подавайте сразу",
                "Разложите порционно и подавайте горячим",
                "Оформите аппетитно и подавайте немедленно",
                "Украсьте специями и подавайте с любимым гарниром",
                "Дайте настояться 2-3 минуты и подавайте",
                "Посыпьте зеленью, подавайте со свежими овощами"
            ],
            'en': ["Arrange nicely and serve warm", "Garnish and serve immediately"],
            'uz': ["Likopchaga joylashtiring va bering", "Darhol dasturxonga torting"]
        }
        return random.choice(templates.get(language, templates['ru']))

    def _get_default_step(self, language: str) -> str:
        """Возвращает дефолтный шаг если ничего не сгенерировано"""
        templates = {
            'ru': "Приготовьте блюдо согласно рецепту",
            'en': "Prepare the dish according to the recipe",
            'uz': "Taomni retsept bo'yicha tayyorlang"
        }
        return templates.get(language, templates['ru'])

    def _generate_tip(self, portions: dict, language: str) -> str:
        """Генерирует полезный совет о блюде"""
        import random

        tips_database = {
            'ru': {
                'high_protein': [
                    "Высокое содержание белка помогает сохранить мышечную массу и ускоряет метаболизм.",
                    "Белок надолго утоляет голод и помогает в восстановлении мышц после тренировок.",
                    "Это блюдо богато белком - идеально для роста мышц и похудения.",
                    "Протеин в составе ускоряет восстановление после физических нагрузок.",
                    "Отличный источник аминокислот для построения мышечной ткани."
                ],
                'high_fiber': [
                    "Клетчатка способствует длительному чувству сытости и улучшает пищеварение.",
                    "Овощи в этом блюде богаты витаминами и минералами для здоровья.",
                    "Клетчатка помогает контролировать уровень сахара в крови.",
                    "Богатые клетчаткой продукты поддерживают здоровье кишечника.",
                    "Это блюдо содержит антиоксиданты, защищающие клетки организма."
                ],
                'balanced': [
                    "Сбалансированное сочетание макронутриентов обеспечивает стабильный уровень энергии.",
                    "Идеальный баланс белков, жиров и углеводов для активного дня.",
                    "Это блюдо даст энергию на несколько часов без тяжести в желудке.",
                    "Оптимальное соотношение нутриентов для восстановления и роста.",
                    "Блюдо содержит все необходимое для поддержания здорового организма."
                ],
                'low_calorie': [
                    "Низкокалорийное блюдо идеально подходит для снижения веса.",
                    "Лёгкое и питательное - можно есть даже на ночь.",
                    "Мало калорий, но много пользы и вкуса.",
                    "Отличный выбор для сушки и рельефа мышц.",
                    "Сытно, вкусно и не навредит фигуре."
                ]
            },
            'en': {
                'high_protein': ["High protein helps build muscle and boost metabolism."],
                'high_fiber': ["Fiber promotes satiety and improves digestion."],
                'balanced': ["Balanced macros provide stable energy levels."],
                'low_calorie': ["Low-calorie and perfect for weight loss."]
            },
            'uz': {
                'high_protein': ["Yuqori protein mushak o'stirish uchun ideal."],
                'high_fiber': ["Tola to'yinganlik va hazm qilishni yaxshilaydi."],
                'balanced': ["Muvozanatli energiya darajasi."],
                'low_calorie': ["Kam kaloriya, vazn yo'qotish uchun."]
            }
        }

        total_protein = sum(p['protein'] for p in portions.values())
        total_carbs = sum(p['carbs'] for p in portions.values())
        total_calories = sum(p['calories'] for p in portions.values())

        if total_protein > 30:
            tip_key = 'high_protein'
        elif total_carbs > 50:
            tip_key = 'high_fiber'
        elif total_calories < 400:
            tip_key = 'low_calorie'
        else:
            tip_key = 'balanced'

        tips = tips_database.get(language, tips_database['ru'])[tip_key]
        return random.choice(tips)

    def _calculate_total_nutrition(self, portions: dict) -> dict:
        """Рассчитывает общую питательность блюда"""
        return {
            'calories': sum(p['calories'] for p in portions.values()),
            'protein': round(sum(p['protein'] for p in portions.values()), 1),
            'fat': round(sum(p['fat'] for p in portions.values()), 1),
            'carbs': round(sum(p['carbs'] for p in portions.values()), 1)
        }

    def _generate_dish_name(self, portions: dict, meal_type: str, language: str) -> str:
        """Генерирует разнообразное название блюда"""
        import random

        if not portions:
            return {"ru": "Полезное блюдо", "en": "Healthy dish", "uz": "Foydali taom"}.get(language, "Healthy dish")

        ingredient_names = []
        for data in portions.values():
            if info := data.get('name'):
                ingredient_names.append(info.get(f'name_{language}', info.get('name_ru', '')))

        if len(ingredient_names) < 2:
            if ingredient_names:
                return ingredient_names[0]
            else:
                return {"ru": "Полезное блюдо", "en": "Healthy dish", "uz": "Foydali taom"}.get(language, "Healthy dish")

        if language == 'ru':
            prefixes = ["", "Аппетитное ", "Сытное ", "Лёгкое ", "Питательное ", "Вкусное ", "Ароматное ", "Полезное ", "Свежее ", "Домашнее ", "Изысканное ", "Нежное ", "Пикантное ", "Сочное ", "Классическое "]
            second = self._to_instrumental_case(ingredient_names[1])
            name = f"{ingredient_names[0]} с {second}"
            return random.choice(prefixes) + name.lower().capitalize()
        elif language == 'en':
            prefixes = ["", "Delicious ", "Hearty ", "Light ", "Nutritious ", "Tasty ", "Aromatic ", "Healthy ", "Fresh ", "Homemade ", "Refined ", "Tender ", "Spicy ", "Juicy ", "Classic "]
            name = f"{ingredient_names[0]} with {ingredient_names[1].lower()}"
            return random.choice(prefixes) + name
        else:
            return f"{ingredient_names[0]} {ingredient_names[1].lower()} bilan"

    def _adjust_to_target(self, meals: list, target_calories: int) -> list:
        """Корректирует приёмы пищи для достижения целевой калорийности"""

        total_current = sum(m['nutrition']['calories'] for m in meals)
        diff = target_calories - total_current

        if abs(diff) < 150:
            return meals

        # Распределяем разницу пропорционально между всеми приёмами
        for meal in meals:
            proportion = meal['nutrition']['calories'] / total_current
            adjustment = int(diff * proportion)
            meal['nutrition']['calories'] += adjustment
            # Корректируем макросы пропорционально
            meal['nutrition']['protein'] = int(meal['nutrition']['protein'] * (1 + adjustment / meal['nutrition']['calories']))
            meal['nutrition']['carbs'] = int(meal['nutrition']['carbs'] * (1 + adjustment / meal['nutrition']['calories']))

        return meals

    def _format_plan(self, meals: list, metabolism: dict, language: str) -> str:
        """
        Форматирует финальный план питания
        СТРОГО по шаблону, БЕЗ смешивания языков
        """

        templates = self.language_templates[language]
        output = []

        # Заголовок
        output.append(templates['title'])
        output.append("")

        # Каждый приём пищи
        meal_types = {
            'breakfast': templates['breakfast'],
            'snack': templates['snack'],
            'snack1': templates['snack'],
            'snack2': templates['snack'],
            'lunch': templates['lunch'],
            'dinner': templates['dinner']
        }

        for meal in meals:
            meal_type_key = meal.get('meal_type', 'breakfast')

            # Заголовок приёма пищи
            output.append(meal_types.get(meal_type_key, templates['breakfast']))
            output.append(f"🍳 {meal['name']}")
            output.append("")

            # Ингредиенты
            output.append(templates['ingredients'])
            for product_key, data in meal['ingredients'].items():
                product_info = data.get('name')
                if product_info:
                    ingredient_name = product_info.get(f'name_{language}', product_info.get('name_ru', ''))
                    output.append(f"🔸 {ingredient_name} {data['grams']}{templates['grams']}")
            output.append("")

            # Приготовление
            output.append(templates['preparation'])
            for j, step in enumerate(meal['steps'], 1):
                # Добавляем эмодзи для каждого шага
                output.append(f"🥘 {step}")
            output.append("")

            # Пищевая ценность
            output.append(templates['nutrition'])
            output.append(f"➡️ {templates['calories']}: {meal['nutrition']['calories']}{templates['kcal']}")
            output.append(f"➡️ {templates['protein']}: {meal['nutrition']['protein']}{templates['g']}")
            output.append(f"➡️ {templates['fat']}: {meal['nutrition']['fat']}{templates['g']}")
            output.append(f"➡️ {templates['carbs']}: {meal['nutrition']['carbs']}{templates['g']}")
            output.append("")

            # Совет
            output.append(templates['tip'])
            output.append(meal['tip'])
            output.append("")

        # Итоговая информация
        total_calories = sum(m['nutrition']['calories'] for m in meals)
        output.append(f"📊 {templates['total']}: ~{total_calories} {templates['kcal']}")
        output.append("")
        output.append("─────────────────────────")
        output.append(templates['ready'])
        output.append("")
        output.append(f"📊 {templates['target']}: {metabolism['target_calories']} {templates['kcal']}")
        output.append(f"📈 {templates.get('recognized', 'Recognized in plan')}: {total_calories} {templates['kcal']}")
        output.append("")
        output.append(templates['metabolism'])
        output.append(f"- BMR: {metabolism['bmr']} {templates['kcal']}")
        output.append(f"- TDEE: {metabolism['tdee']} {templates['kcal']}")
        if 'water_ml' in metabolism:
            water_liters = metabolism['water_ml'] / 1000
            water_text = templates.get('water', 'Water')
            per_day = templates.get('per_day', 'per day')
            output.append(f"- 💧 {water_text}: {water_liters:.1f}L {per_day}")
        output.append("")

        # Персональный совет на основе цели
        goal = metabolism.get('goal', 'maintain')
        goal_advice = self._get_goal_advice(goal, language)
        if goal_advice:
            output.append(f"🎯 {goal_advice}")
            output.append("")

        output.append(templates['advice'])
        output.append("")
        output.append(templates['enjoy'])

        return "\n".join(output)

    def _get_goal_advice(self, goal: str, language: str) -> str:
        """Даёт персональный совет на основе цели с вариациями"""
        advice = {
            'ru': {
                'lose_weight': [
                    "Для похудения: пейте больше воды и избегайте перекусов после ужина.",
                    "Дефицит калорий работает! Ешьте медленно и наслаждайтесь каждым кусочком.",
                    "Увеличьте количество овощей в рационе - они низкокалорийны и питательны.",
                    "Спите 7-8 часов - недосып замедляет метаболизм и усиливает аппетит.",
                    "Готовьте дома чаще - так вы контролируете калорийность и качество продуктов.",
                    "Замените быстрые углеводы на медленные - они дольше насыщают."
                ],
                'gain_muscle': [
                    "Для роста мышц: увеличьте порции белка и тренируйтесь 3-4 раза в неделю.",
                    "Профицит калорий + силовые тренировки = рост мышечной массы!",
                    "Ешьте белок после тренировки - это оптимальное время для восстановления мышц.",
                    "Не забывайте про углеводы - они дают энергию для интенсивных тренировок.",
                    "Прогрессивная перегрузка - ключ к росту. Постепенно увеличивайте нагрузку.",
                    "Отдых важен! Мышцы растут во время восстановления, а не тренировки."
                ],
                'maintain': [
                    "Для поддержания формы: следуйте плану и занимайтесь спортом регулярно.",
                    "Баланс - ключ к успеху. Ешьте разнообразно и тренируйтесь умеренно.",
                    "Регулярность важнее интенсивности - занимайтесь спортом 3-4 раза в неделю.",
                    "Поддерживайте водный баланс - пейте воду в течение всего дня.",
                    "Слушайте своё тело и корректируйте план при необходимости.",
                    "Здоровое питание - это образ жизни, а не временная диета."
                ]
            },
            'en': {
                'lose_weight': [
                    "For weight loss: drink more water and avoid snacks after dinner.",
                    "Calorie deficit works! Eat slowly and enjoy every bite.",
                    "Add more vegetables - they're low-calorie and nutritious.",
                    "Sleep 7-8 hours - lack of sleep slows metabolism and increases appetite.",
                    "Cook at home more often to control calories and quality.",
                    "Replace simple carbs with complex ones - they keep you full longer."
                ],
                'gain_muscle': [
                    "For muscle gain: increase protein portions and train 3-4 times a week.",
                    "Calorie surplus + strength training = muscle growth!",
                    "Eat protein after workouts - optimal time for muscle recovery.",
                    "Don't forget carbs - they provide energy for intense training.",
                    "Progressive overload is key. Gradually increase your load.",
                    "Rest matters! Muscles grow during recovery, not training."
                ],
                'maintain': [
                    "To maintain: follow the plan and exercise regularly.",
                    "Balance is key. Eat varied and train moderately.",
                    "Consistency beats intensity - exercise 3-4 times weekly.",
                    "Stay hydrated - drink water throughout the day.",
                    "Listen to your body and adjust the plan as needed.",
                    "Healthy eating is a lifestyle, not a temporary diet."
                ]
            },
            'uz': {
                'lose_weight': [
                    "Vazn yo'qotish: ko'proq suv iching.",
                    "Kaloriya kamayishi ishlaydi! Sekinroq ovqatlaning.",
                    "Ko'proq sabzavot iste'mol qiling - ular kam kaloriyali.",
                    "7-8 soat uxlang - uyqusizlik metabolizmni sekinlashtiradi.",
                    "Uyda tayyorlang - kaloriyani nazorat qiling.",
                    "Oddiy uglevodlarni murakkablar bilan almashtiring."
                ],
                'gain_muscle': [
                    "Mushak: protein ko'paytiring.",
                    "Kaloriya ortishi + kuch mashqlari = mushak o'sishi!",
                    "Mashqdan keyin protein iste'mol qiling.",
                    "Uglevodlarni unutmang - energiya beradi.",
                    "Bosqichma-bosqich yukni oshiring.",
                    "Dam olish muhim! Mushaklar tiklanishda o'sadi."
                ],
                'maintain': [
                    "Shakl: rejaga amal qiling.",
                    "Muvozanat - muvaffaqiyat kaliti.",
                    "Muntazamlik intensivlikdan muhimroq.",
                    "Suv balansini saqlang.",
                    "Tanangizga quloq soling.",
                    "Sog'lom ovqatlanish - turmush tarzi."
                ]
            }
        }
        goal_advice = advice.get(language, advice['ru']).get(goal, [])
        return random.choice(goal_advice) if goal_advice else ''

    def _load_templates(self) -> dict:
        """Загружает языковые шаблоны"""
        return {
            'ru': {
                'title': '🍽 ВАШ ПЕРСОНАЛЬНЫЙ ПЛАН ПИТАНИЯ',
                'breakfast': '🌅 ЗАВТРАК',
                'snack': '🍎 ПЕРЕКУС',
                'lunch': '🌞 ОБЕД',
                'dinner': '🌙 УЖИН',
                'ingredients': '🛒 Ингредиенты:',
                'preparation': '👨‍🍳 Приготовление:',
                'nutrition': '📊 ПИЩЕВАЯ ЦЕННОСТЬ',
                'calories': 'Калорийность',
                'protein': 'Белки',
                'fat': 'Жиры',
                'carbs': 'Углеводы',
                'tip': '💡 ПОЛЕЗНЫЙ СОВЕТ',
                'ready': '✅ ПЛАН ПИТАНИЯ ГОТОВ!',
                'target': 'Целевая калорийность',
                'total': 'ИТОГО ЗА ДЕНЬ',
                'metabolism': '🔥 Ваш метаболизм:',
                'advice': '💡 Совет: Следуйте плану для достижения наилучших результатов!',
                'enjoy': '🍽 Приятного аппетита!',
                'kcal': 'ккал',
                'g': 'г',
                'grams': 'г',
                'recognized': 'Распознано в плане',
                'water': 'Вода',
                'per_day': 'в день'
            },
            'en': {
                'title': '🍽 YOUR PERSONAL NUTRITION PLAN',
                'breakfast': '🌅 BREAKFAST',
                'snack': '🍎 SNACK',
                'lunch': '🍽 LUNCH',
                'dinner': '🌙 DINNER',
                'ingredients': '🛒 Ingredients:',
                'preparation': '👨‍🍳 Preparation:',
                'nutrition': '📊 NUTRITIONAL VALUE',
                'calories': 'Calories',
                'protein': 'Protein',
                'fat': 'Fat',
                'carbs': 'Carbs',
                'tip': '💡 TIP',
                'ready': '✅ PLAN READY!',
                'target': 'Target calories',
                'total': 'Total in plan',
                'metabolism': '🔥 Your metabolism:',
                'advice': '💡 Tip: Follow the plan for best results!',
                'enjoy': '🍽 Enjoy your meal!',
                'kcal': 'kcal',
                'g': 'g',
                'grams': 'g',
                'recognized': 'Recognized in plan',
                'water': 'Water',
                'per_day': 'per day'
            },
            'uz': {
                'title': '🍽 SIZNING SHAXSIY OVQATLANISH REJANGIZ',
                'breakfast': '🌅 NONUSHTA',
                'snack': '🍎 GAZAK',
                'lunch': '🍽 TUSHLIK',
                'dinner': '🌙 KECHKI OVQAT',
                'ingredients': '🛒 Ingredientlar:',
                'preparation': '👨‍🍳 Tayyorlash:',
                'nutrition': '📊 OZUQAVIY QIYMAT',
                'calories': 'Kaloriya',
                'protein': 'Oqsil',
                'fat': "Yog'",
                'carbs': 'Uglevodlar',
                'tip': '💡 MASLAHAT',
                'ready': '✅ REJA TAYYOR!',
                'target': 'Maqsadli kaloriya',
                'total': 'Rejada jami',
                'metabolism': '🔥 Sizning metabolizmingiz:',
                'advice': '💡 Maslahat: Eng yaxshi natijalar uchun rejaga amal qiling!',
                'enjoy': '🍽 Yoqimli ishtaha!',
                'kcal': 'kkal',
                'g': 'g',
                'grams': 'g',
                'recognized': 'Rejada aniqlangan',
                'water': 'Suv',
                'per_day': 'kuniga'
            }
        }

    def generate_fallback_plan(self, profile: dict, language: str = "ru") -> str:
        """
        Генерирует базовый план питания в случае ошибки
        """
        if language == "ru":
            return f"""🍽 **БАЗОВЫЙ ПЛАН ПИТАНИЯ**

📊 **Ваши параметры:**
• Возраст: {profile.get('age', 25)} лет
• Вес: {profile.get('weight', 70)} кг
• Цель: {profile.get('goal', 'maintain')}

🥗 **ЗАВТРАК (7:00-9:00)**
• Овсянка на воде (50г)
• Яйца вареные (2 шт)
• Банан (1 шт)
• Кофе/чай без сахара
📊 ~400 ккал | Б: 25г Ж: 12г У: 45г

🍴 **ОБЕД (13:00-15:00)**
• Куриная грудка (150г)
• Рис белый (100г)
• Овощной салат (200г)
• Оливковое масло (1 ч.л.)
📊 ~450 ккал | Б: 40г Ж: 10г У: 50г

🌮 **УЖИН (18:00-20:00)**
• Рыба/морепродукты (150г)
• Гречка (80г)
• Овощи на пару (200г)
📊 ~380 ккал | Б: 35г Ж: 8г У: 40г

💧 **Рекомендации:**
• Пейте 2-2.5 литра воды в день
• Принимайте витамины
• Избегайте фаст-фуда и сладкого

✅ Этот базовый план подходит для большинства целей. Для персонализированного плана попробуйте снова через некоторое время."""

        elif language == "en":
            return f"""🍽 **BASIC MEAL PLAN**

📊 **Your parameters:**
• Age: {profile.get('age', 25)} years
• Weight: {profile.get('weight', 70)} kg
• Goal: {profile.get('goal', 'maintain')}

🥗 **BREAKFAST (7:00-9:00 AM)**
• Oatmeal with water (50g)
• Boiled eggs (2 pcs)
• Banana (1 pc)
• Coffee/tea without sugar
📊 ~400 kcal | P: 25g F: 12g C: 45g

🍴 **LUNCH (1:00-3:00 PM)**
• Chicken breast (150g)
• White rice (100g)
• Vegetable salad (200g)
• Olive oil (1 tsp)
📊 ~450 kcal | P: 40g F: 10g C: 50g

🌮 **DINNER (6:00-8:00 PM)**
• Fish/seafood (150g)
• Buckwheat (80g)
• Steamed vegetables (200g)
📊 ~380 kcal | P: 35g F: 8g C: 40g

💧 **Recommendations:**
• Drink 2-2.5 liters of water per day
• Take vitamins
• Avoid fast food and sweets

✅ This basic plan is suitable for most goals. For a personalized plan, try again later."""

        else:  # uz
            return f"""🍽 **ASOSIY OVQATLANISH REJASI**

📊 **Sizning parametrlaringiz:**
• Yosh: {profile.get('age', 25)} yil
• Vazn: {profile.get('weight', 70)} kg
• Maqsad: {profile.get('goal', 'maintain')}

🥗 **NONUSHTA (7:00-9:00)**
• Suv ustida jo'xori (50g)
• Qaynatilgan tuxum (2 dona)
• Banan (1 dona)
• Kofe/choy shakarsiz
📊 ~400 kkal | O: 25g Y: 12g U: 45g

🍴 **TUSHLIK (13:00-15:00)**
• Tovuq ko'kragi (150g)
• Oq guruch (100g)
• Sabzavot salati (200g)
• Zaytun moyi (1 ch.l.)
📊 ~450 kkal | O: 40g Y: 10g U: 50g

🌮 **KECHKI OVQAT (18:00-20:00)**
• Baliq/dengiz mahsulotlari (150g)
• Grechka (80g)
• Bug'da pishirilgan sabzavotlar (200g)
📊 ~380 kkal | O: 35g Y: 8g U: 40g

💧 **Tavsiyalar:**
• Kuniga 2-2.5 litr suv iching
• Vitaminlar qabul qiling
• Fast-fud va shirinliklardan saqlaning

✅ Bu asosiy reja ko'pchilik maqsadlar uchun mos keladi. Shaxsiy reja uchun keyinroq qayta urinib ko'ring."""


class IntelligentWorkoutPlanner:
    """
    Интеллектуальная система планирования тренировок
    """

    def __init__(self):
        self.exercise_db = ExerciseDatabase()
        self.language_templates = self._load_templates()

    def generate_workout_plan(self, profile: dict, workout_info: dict, language: str = "ru") -> str:
        """
        Генерирует план тренировки

        Args:
            profile: {age, weight, height, gender, goal, activity_level}
            workout_info: {workout_type, equipment, duration, focus_areas}
            language: ru/en/uz
        """

        # Определяем уровень опыта
        level = profile.get('activity_level', 'intermediate')

        # Получаем тип тренировки
        workout_type = workout_info.get('workout_type', 'full_body')

        # Подбираем упражнения
        exercises = self._select_exercises(
            workout_type=workout_type,
            equipment=workout_info.get('equipment', 'none'),
            level=level,
            focus_areas=workout_info.get('focus_areas', [])
        )

        # Создаём структуру тренировки
        workout_structure = self._build_workout_structure(exercises, level, language)

        # Форматируем план
        formatted_plan = self._format_workout_plan(
            workout_structure=workout_structure,
            workout_type=workout_type,
            level=level,
            language=language
        )

        # AI-перевод на выбранный язык
        if language != "ru":
            formatted_plan = translate_with_ai(formatted_plan, language)

        return formatted_plan

    def _select_exercises(self, workout_type: str, equipment: str, level: str, focus_areas: list) -> list:
        """Подбирает упражнения для тренировки БЕЗ ПОВТОРОВ"""

        all_exercises = ExerciseDatabase.get_all_exercises()

        # Фильтруем по оборудованию
        if equipment != 'all':
            all_exercises = [e for e in all_exercises if e['equipment'] in [equipment, 'none']]

        selected = []
        used_keys = set()  # Отслеживаем использованные упражнения

        if workout_type == 'full_body':
            # Полная тренировка тела - разные группы мышц
            muscle_groups = ['chest', 'back', 'legs', 'shoulders', 'abs']
            for group in muscle_groups:
                group_exercises = [e for e in all_exercises
                                 if group in e['muscle_groups'] and e['key'] not in used_keys]
                if group_exercises:
                    exercise = random.choice(group_exercises)  # РАЗНООБРАЗИЕ!
                    selected.append(exercise)
                    used_keys.add(exercise['key'])

        elif workout_type == 'upper_body':
            muscle_groups = ['chest', 'back', 'shoulders', 'biceps', 'triceps']
            for group in muscle_groups:
                group_exercises = [e for e in all_exercises
                                 if group in e['muscle_groups'] and e['key'] not in used_keys]
                if group_exercises:
                    exercise = random.choice(group_exercises)  # РАЗНООБРАЗИЕ!
                    selected.append(exercise)
                    used_keys.add(exercise['key'])

        elif workout_type == 'lower_body':
            # Для ног выбираем больше упражнений - 4-5 штук
            leg_exercises = [e for e in all_exercises
                           if ('legs' in e['muscle_groups'] or 'glutes' in e['muscle_groups'])
                           and e['key'] not in used_keys]
            if leg_exercises:
                random.shuffle(leg_exercises)
                # Выбираем 4-5 упражнений для полноценной тренировки ног
                for ex in leg_exercises[:5]:
                    if ex['key'] not in used_keys:
                        selected.append(ex)
                        used_keys.add(ex['key'])

        elif workout_type == 'cardio':
            cardio_exercises = [e for e in all_exercises if 'cardio' in e['muscle_groups']]
            random.shuffle(cardio_exercises)  # РАЗНООБРАЗИЕ!
            selected = cardio_exercises[:3] if len(cardio_exercises) >= 3 else cardio_exercises

        else:
            # Фокус на конкретных областях
            for area in focus_areas:
                area_exercises = [e for e in all_exercises
                                if area in e['muscle_groups'] and e['key'] not in used_keys]
                if area_exercises:
                    exercise = area_exercises[0]
                    selected.append(exercise)
                    used_keys.add(exercise['key'])

        # Перемещаем планку в конец списка (если она есть)
        if selected:
            plank_exercises = []
            other_exercises = []
            for ex in selected:
                # Проверяем, является ли упражнение планкой
                key = ex.get('key', '')
                name_ru = ex.get('name_ru', '').lower()
                if 'планка' in key or 'планка' in name_ru or 'plank' in key.lower():
                    plank_exercises.append(ex)
                else:
                    other_exercises.append(ex)
            # Планка всегда в конце
            selected = other_exercises + plank_exercises

        return selected if selected else all_exercises[:5]

    def _build_workout_structure(self, exercises: list, level: str, language: str) -> list:
        """Строит структуру тренировки с подходами и повторениями"""

        structure = []

        for exercise in exercises:
            progression = exercise.get('progression', {}).get(level, {})

            exercise_plan = {
                'name': exercise.get(f'name_{language}', exercise.get('name_ru')),
                'sets': progression.get('sets', 3),
                'reps': progression.get('reps', '10-12'),
                'rest': progression.get('rest_seconds', 60),
                'technique': exercise.get(f'technique_{language}', exercise.get('technique_ru')),
                'mistakes': exercise.get(f'common_mistakes_{language}', exercise.get('common_mistakes_ru', [])),
                'muscle_groups': exercise.get('muscle_groups', []),  # ВАЖНО для объяснений!
                'duration_minutes': progression.get('duration_minutes'),
                'duration_seconds': progression.get('duration_seconds')
            }

            structure.append(exercise_plan)

        return structure

    def _format_workout_plan(self, workout_structure: list, workout_type: str, level: str, language: str) -> str:
        """Форматирует план тренировки"""

        templates = self.language_templates[language]
        output = []

        # Заголовок
        output.append(templates['title'])
        output.append("")

        # Тип тренировки
        workout_names = {
            'full_body': templates.get('full_body', 'Full body'),
            'upper_body': templates.get('upper_body', 'Upper body'),
            'lower_body': templates.get('lower_body', 'Lower body'),
            'cardio': templates.get('cardio', 'Cardio')
        }
        output.append(f"📋 {templates['type']}: {workout_names.get(workout_type, workout_type)}")
        output.append(f"⭐ {templates['level']}: {level}")
        output.append("")

        # Упражнения
        for i, exercise in enumerate(workout_structure, 1):
            output.append("─────────────────────────")
            output.append(f"{i}. {exercise['name']}")
            output.append("")

            if exercise.get('duration_minutes'):
                output.append(f"⏱ {templates['duration']}: {exercise['duration_minutes']} {templates['minutes']}")
            elif exercise.get('duration_seconds'):
                output.append(f"⏱ {templates['duration']}: {exercise['duration_seconds']} {templates['seconds']}")
            else:
                output.append(f"🔢 {templates['sets']}: {exercise['sets']}")
                output.append(f"🔁 {templates['reps']}: {exercise['reps']}")

            output.append(f"⏸ {templates['rest']}: {exercise['rest']} {templates['seconds']}")
            output.append("")

            # Техника
            output.append(f"✅ {templates['technique']}:")
            output.append(exercise['technique'])
            output.append("")

            # Ошибки
            if exercise.get('mistakes'):
                output.append(f"❌ {templates['mistakes']}:")
                for mistake in exercise['mistakes'][:3]:
                    output.append(f"🔸 {mistake}")
                output.append("")

            # ОБЪЯСНЕНИЕ: Для чего это упражнение
            output.append(f"ℹ️  {templates.get('explanation', 'Объяснение')}:")
            explanation = self._get_exercise_explanation(exercise, language)
            output.append(explanation)
            output.append("")

        # Итоги
        output.append("═════════════════════════")
        output.append(templates['ready'])
        output.append("")
        output.append(templates['advice'])
        output.append(templates['good_luck'])

        return "\n".join(output)

    def _get_exercise_explanation(self, exercise: dict, language: str) -> str:
        """Генерирует объяснение для чего нужно упражнение"""

        explanations = {
            'ru': {
                'chest': "Это упражнение развивает грудные мышцы, делает торс шире и увеличивает силу верхней части тела.",
                'back': "Укрепляет мышцы спины, улучшает осанку и помогает предотвратить боли в пояснице.",
                'legs': "Развивает мышцы ног и ягодиц, улучшает баланс и увеличивает силу нижней части тела.",
                'shoulders': "Формирует широкие плечи, улучшает подвижность плечевого сустава.",
                'biceps': "Увеличивает объем рук, улучшает силу хвата и помогает в других упражнениях.",
                'triceps': "Делает руки более рельефными, увеличивает силу в жимовых движениях.",
                'abs': "Укрепляет мышцы кора, улучшает стабильность тела и помогает в других упражнениях.",
                'cardio': "Улучшает выносливость, сжигает калории и укрепляет сердечно-сосудистую систему.",
                'glutes': "Развивает ягодичные мышцы, улучшает форму нижней части тела."
            },
            'en': {
                'chest': "This exercise develops chest muscles, makes torso wider and increases upper body strength.",
                'back': "Strengthens back muscles, improves posture and helps prevent lower back pain.",
                'legs': "Develops leg and glute muscles, improves balance and increases lower body strength.",
                'shoulders': "Builds broad shoulders, improves shoulder joint mobility.",
                'biceps': "Increases arm size, improves grip strength and helps in other exercises.",
                'triceps': "Makes arms more defined, increases strength in pressing movements.",
                'abs': "Strengthens core muscles, improves body stability and helps in other exercises.",
                'cardio': "Improves endurance, burns calories and strengthens cardiovascular system.",
                'glutes': "Develops glute muscles, improves lower body shape."
            },
            'uz': {
                'chest': "Bu mashq ko'krak mushaklarini rivojlantiradi, tanani kengaytiradi va yuqori tananing kuchini oshiradi.",
                'back': "Orqa mushaklarni mustahkamlaydi, duruslikni yaxshilaydi va bel og'rig'ining oldini oladi.",
                'legs': "Oyoq va dumba mushaklarni rivojlantiradi, balansni yaxshilaydi va pastki tananing kuchini oshiradi.",
                'shoulders': "Keng yelkalarni shakllantiradi, yelka bo'g'imining harakatchanligini yaxshilaydi.",
                'biceps': "Qo'llarning hajmini oshiradi, tutish kuchini yaxshilaydi va boshqa mashqlarda yordam beradi.",
                'triceps': "Qo'llarni relyefli qiladi, surish harakatlarida kuchni oshiradi.",
                'abs': "Kor mushaklarni mustahkamlaydi, tananing barqarorligini yaxshilaydi.",
                'cardio': "Chidamlilikni yaxshilaydi, kaloriya yoqadi va yurak-qon tomir tizimini mustahkamlaydi.",
                'glutes': "Dumba mushaklarini rivojlantiradi, pastki tananing shaklini yaxshilaydi."
            }
        }

        lang_expl = explanations.get(language, explanations['ru'])
        muscle_groups = exercise.get('muscle_groups', [])

        # Выбираем объяснение по первой группе мышц
        if muscle_groups:
            main_group = muscle_groups[0]
            explanation = lang_expl.get(main_group, '')
            if explanation:
                return explanation

        # Если не нашли по первой группе, берем вторую
        if len(muscle_groups) > 1:
            second_group = muscle_groups[1]
            explanation = lang_expl.get(second_group, '')
            if explanation:
                return explanation

        # По умолчанию
        return lang_expl.get('chest', 'Полезное упражнение для развития силы и выносливости.')

    def _load_templates(self) -> dict:
        """Загружает языковые шаблоны"""
        return {
            'ru': {
                'title': '🏋️ ВАШ ПЕРСОНАЛЬНЫЙ ПЛАН ТРЕНИРОВКИ',
                'type': 'Тип тренировки',
                'level': 'Уровень',
                'full_body': 'Все тело',
                'upper_body': 'Верх тела',
                'lower_body': 'Низ тела',
                'cardio': 'Кардио',
                'sets': 'Подходы',
                'reps': 'Повторения',
                'rest': 'Отдых',
                'duration': 'Длительность',
                'minutes': 'мин',
                'seconds': 'сек',
                'technique': 'Техника выполнения',
                'mistakes': 'Частые ошибки',
                'explanation': 'Для чего это упражнение',
                'ready': '✅ ПЛАН ГОТОВ!',
                'advice': '💡 Совет: Выполняйте упражнения с правильной техникой для максимального эффекта!',
                'good_luck': '💪 Удачной тренировки!'
            },
            'en': {
                'title': '🏋️ YOUR PERSONAL WORKOUT PLAN',
                'type': 'Workout type',
                'level': 'Level',
                'full_body': 'Full body',
                'upper_body': 'Upper body',
                'lower_body': 'Lower body',
                'cardio': 'Cardio',
                'sets': 'Sets',
                'reps': 'Reps',
                'rest': 'Rest',
                'duration': 'Duration',
                'minutes': 'min',
                'seconds': 'sec',
                'technique': 'Technique',
                'mistakes': 'Common mistakes',
                'explanation': 'Why this exercise',
                'ready': '✅ PLAN READY!',
                'advice': '💡 Tip: Perform exercises with proper technique for maximum effect!',
                'good_luck': '💪 Good luck with your workout!'
            },
            'uz': {
                'title': '💪 SIZNING SHAXSIY MASHG\'ULOT REJANGIZ',
                'type': "Mashg'ulot turi",
                'level': 'Daraja',
                'full_body': 'Butun tana',
                'upper_body': 'Yuqori tana',
                'lower_body': 'Pastki tana',
                'cardio': 'Kardio',
                'sets': 'Setlar',
                'reps': 'Takrorlar',
                'rest': 'Dam olish',
                'duration': 'Davomiyligi',
                'minutes': 'daq',
                'seconds': 'son',
                'technique': 'Bajarish texnikasi',
                'mistakes': 'Keng tarqalgan xatolar',
                'explanation': 'Nima uchun bu mashq',
                'ready': '✅ REJA TAYYOR!',
                'advice': "💡 Maslahat: Maksimal samaradorlik uchun mashqlarni to'g'ri texnika bilan bajaring!",
                'good_luck': "💪 Mashg'ulotingiz baxtiyor bo'lsin!"
            }
        }

    def generate_fallback_plan(self, profile: dict, language: str = "ru") -> str:
        """
        Генерирует базовый план тренировки в случае ошибки
        """
        if language == "ru":
            return f"""💪 **БАЗОВЫЙ ПЛАН ТРЕНИРОВКИ**

📊 **Ваши параметры:**
• Возраст: {profile.get('age', 25)} лет
• Вес: {profile.get('weight', 70)} кг
• Уровень: {profile.get('activity_level', 'intermediate')}

🏋️ **РАЗМИНКА (5 минут)**
• Легкий бег на месте - 2 мин
• Вращения руками - 20 раз
• Приседания без веса - 15 раз
• Наклоны в стороны - 10 раз каждую сторону

💪 **ОСНОВНАЯ ЧАСТЬ (30 минут)**

**1. Приседания**
• 3 подхода по 15-20 раз
• Отдых 60 секунд

**2. Выпады**
• 3 подхода по 10 раз на каждую ногу
• Отдых 60 секунд

**3. Жим ногами / Приседания с весом**
• 3 подхода по 12-15 раз
• Отдых 90 секунд

**4. Сгибания ног лёжа**
• 3 подхода по 12-15 раз
• Отдых 60 секунд

**5. Планка**
• 3 подхода по 30-45 секунд
• Отдых 45 секунд

🧘 **ЗАМИНКА (5 минут)**
• Растяжка всех групп мышц
• Дыхательные упражнения

💧 **Рекомендации:**
• Пейте воду между подходами
• Следите за техникой выполнения
• Отдыхайте 48 часов между тренировками

✅ Это базовая программа для начального уровня. Для персонализированной тренировки попробуйте снова позже."""

        elif language == "en":
            return f"""💪 **BASIC WORKOUT PLAN**

📊 **Your parameters:**
• Age: {profile.get('age', 25)} years
• Weight: {profile.get('weight', 70)} kg
• Level: {profile.get('activity_level', 'intermediate')}

🏋️ **WARM-UP (5 minutes)**
• Light jogging in place - 2 min
• Arm circles - 20 times
• Bodyweight squats - 15 times
• Side bends - 10 times each side

💪 **MAIN WORKOUT (30 minutes)**

**1. Squats**
• 3 sets x 15-20 reps
• Rest 60 seconds

**2. Lunges**
• 3 sets x 10 reps each leg
• Rest 60 seconds

**3. Leg Press / Weighted Squats**
• 3 sets x 12-15 reps
• Rest 90 seconds

**4. Lying Leg Curls**
• 3 sets x 12-15 reps
• Rest 60 seconds

**5. Plank**
• 3 sets x 30-45 seconds
• Rest 45 seconds

🧘 **COOL DOWN (5 minutes)**
• Stretch all muscle groups
• Breathing exercises

💧 **Recommendations:**
• Drink water between sets
• Focus on proper form
• Rest 48 hours between workouts

✅ This is a basic program for beginners. For a personalized workout, try again later."""

        else:  # uz
            return f"""💪 **ASOSIY MASHG'ULOT REJASI**

📊 **Sizning parametrlaringiz:**
• Yosh: {profile.get('age', 25)} yil
• Vazn: {profile.get('weight', 70)} kg
• Daraja: {profile.get('activity_level', 'intermediate')}

🏋️ **ISINISH (5 daqiqa)**
• O'rinda yugurish - 2 daq
• Qo'llarni aylantirish - 20 marta
• Vaznsiz cho'kish - 15 marta
• Yon tomonga egilish - har tomonga 10 marta

💪 **ASOSIY QISM (30 daqiqa)**

**1. Cho'kish**
• 3 set x 15-20 takror
• Dam olish 60 soniya

**2. Qadam tashlash**
• 3 set x har oyoqqa 10 takror
• Dam olish 60 soniya

**3. Oyoq pressi / Vaznli cho'kish**
• 3 set x 12-15 takror
• Dam olish 90 soniya

**4. Yotgan holatda oyoq bukish**
• 3 set x 12-15 takror
• Dam olish 60 soniya

**5. Planka**
• 3 set x 30-45 soniya
• Dam olish 45 soniya

🧘 **YOPISH (5 daqiqa)**
• Barcha mushak guruhlarini cho'zish
• Nafas olish mashqlari

💧 **Tavsiyalar:**
• Setlar orasida suv iching
• To'g'ri texnikaga e'tibor bering
• Mashg'ulotlar orasida 48 soat dam oling

✅ Bu boshlang'ich daraja uchun asosiy dastur. Shaxsiy mashg'ulot uchun keyinroq qayta urinib ko'ring."""
