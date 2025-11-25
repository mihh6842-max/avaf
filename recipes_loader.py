import random
import json
import os
import logging

logger = logging.getLogger(__name__)

class RecipesLoader:
    def __init__(self):
        self.recipes = self._load_from_books()

    def _load_from_books(self):
        """Загрузка рецептов из папки book/ с разделением по целям"""
        recipes = {
            "gain_weight": {"breakfast": [], "lunch": [], "dinner": []},
            "lose_weight": {"breakfast": [], "lunch": [], "dinner": []},
            "maintain": {"breakfast": [], "lunch": [], "dinner": []}
        }
        book_path = "book"

        # Проверяем существование папки
        if not os.path.exists(book_path):
            print(f"[WARNING] Folder '{book_path}' not found, using empty recipes")
            return recipes

        # Загружаем из каждой папки (худеем, поддержание, набор веса)
        for goal_folder in os.listdir(book_path):
            folder_path = os.path.join(book_path, goal_folder)
            if not os.path.isdir(folder_path):
                continue

            # Загружаем файлы breakfast.json, lunch.json, dinner.json
            meal_files = {
                "breakfast": "breakfast.json",
                "lunch": "lunch.json",
                "dinner": "dinner.json"
            }

            for meal_type, filename in meal_files.items():
                filepath = os.path.join(folder_path, filename)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Сохраняем рецепты под нужной целью
                            if goal_folder in recipes:
                                recipes[goal_folder][meal_type].extend(data)
                    except:
                        pass

        return recipes

    def _filter_by_meal(self, goal, meal_type):
        """Фильтр по цели и типу приема пищи"""
        # Поддержка как русских, так и английских названий
        meal_map = {
            "завтрак": "breakfast",
            "обед": "lunch",
            "ужин": "dinner",
            "breakfast": "breakfast",
            "lunch": "lunch",
            "dinner": "dinner"
        }

        # Маппинг целей
        goal_map = {
            'gain_muscle': 'gain_weight',
            'набор_массы': 'gain_weight',
            'massa_oshirish': 'gain_weight',
            'lose_weight': 'lose_weight',
            'похудение': 'lose_weight',
            'vazn_yoqotish': 'lose_weight',
            'maintain': 'maintain',
            'поддержание': 'maintain',
            'saqlash': 'maintain'
        }

        eng_type = meal_map.get(meal_type.lower(), meal_type)
        eng_goal = goal_map.get(goal, 'maintain')

        # Получаем рецепты для конкретной цели
        if eng_goal in self.recipes and eng_type in self.recipes[eng_goal]:
            return self.recipes[eng_goal][eng_type]
        return []

    def search_by_ingredients(self, goal, meal_type, ingredients):
        filtered = self._filter_by_meal(goal, meal_type)
        if not filtered or not ingredients:
            return []

        # Словарь синонимов для продуктов
        synonyms = {
            "мясо": ["говядина", "свинина", "баранина", "фарш"],
            "курица": ["куриный", "курице", "курицы"],
            "рыба": ["треска", "лосось", "тунец", "семга"],
            "яйца": ["яйцо", "яичный"],
            "рис": ["рисовый", "рисом"],
            "гречка": ["гречневая", "гречку"],
            "картофель": ["картошка", "картофеля"],
            "молоко": ["молочный", "молока"],
        }

        # Ищем рецепты с совпадающими ингредиентами
        matched = []
        matched_set = set()

        for recipe in filtered:
            recipe_ings = recipe.get("Ингредиенты", [])
            all_ings = " ".join(recipe_ings).lower()

            # Проверяем каждый ингредиент пользователя
            for user_ing in ingredients:
                user_ing_lower = user_ing.lower().strip()

                # Получаем синонимы
                search_words = [user_ing_lower]
                if user_ing_lower in synonyms:
                    search_words.extend(synonyms[user_ing_lower])

                # Для каждого слова создаем варианты окончаний
                search_variants = []
                for word in search_words:
                    search_variants.extend([
                        word,
                        word + "а", word + "е", word + "и", word + "ы", word + "ом", word + "ой",
                        word[:-1] if len(word) > 3 else word,
                    ])

                # Ищем совпадение
                if any(variant in all_ings for variant in search_variants):
                    recipe_id = id(recipe)
                    if recipe_id not in matched_set:
                        matched.append(recipe)
                        matched_set.add(recipe_id)
                    break

        # Если нашли совпадения - возвращаем их
        if matched:
            converted = [self._convert_to_old_format(r) for r in matched]
            return random.sample(converted, min(10, len(converted)))

        # Если нет - возвращаем случайные
        converted = [self._convert_to_old_format(r) for r in filtered]
        return random.sample(converted, min(5, len(converted)))

    def get_recipes(self, goal, meal_type, count=10):
        filtered = self._filter_by_meal(goal, meal_type)
        if not filtered:
            return []
        # Конвертируем в старый формат
        converted = [self._convert_to_old_format(r) for r in filtered]
        return random.sample(converted, min(count, len(converted)))

    def get_recipe(self, goal, meal_type):
        filtered = self._filter_by_meal(goal, meal_type)
        if not filtered:
            return self._create_default_recipe(meal_type)
        recipe = random.choice(filtered)
        return self._convert_to_old_format(recipe)

    def _generate_cooking_instructions(self, dish_name, ingredients_list):
        """Генерирует детальные инструкции приготовления на основе названия блюда"""
        # База знаний для разных типов блюд
        cooking_templates = {
            "омлет": [
                "Взбейте яйца с молоком в глубокой миске до однородности.",
                "Добавьте соль и перец по вкусу.",
                "Разогрейте сковороду с маслом на среднем огне.",
                "Добавьте основные ингредиенты и обжарьте 2-3 минуты.",
                "Влейте яичную смесь и готовьте под крышкой 5-7 минут до готовности.",
                "Подавайте горячим, украсив зеленью."
            ],
            "салат": [
                "Тщательно промойте все овощи и зелень.",
                "Нарежьте ингредиенты нужного размера.",
                "Выложите компоненты в салатник.",
                "Приготовьте заправку и перемешайте.",
                "Дайте настояться 10 минут перед подачей."
            ],
            "каша": [
                "Промойте крупу под проточной водой.",
                "Залейте водой в пропорции 1:2 и доведите до кипения.",
                "Уменьшите огонь и варите под крышкой 15-20 минут.",
                "Добавьте соль, масло и дополнительные ингредиенты.",
                "Дайте настояться 5 минут под крышкой."
            ],
            "суп": [
                "Доведите бульон или воду до кипения.",
                "Добавьте нарезанные овощи и мясо.",
                "Варите на среднем огне 20-30 минут.",
                "Добавьте специи и зелень за 5 минут до готовности.",
                "Подавайте горячим со сметаной."
            ],
            "мясо": [
                "Подготовьте мясо: промойте и нарежьте порционными кусками.",
                "Приправьте солью, перцем и специями.",
                "Обжарьте на сильном огне до золотистой корочки.",
                "Добавьте овощи и тушите под крышкой 30-40 минут.",
                "Проверьте готовность и подавайте с гарниром."
            ],
            "рыба": [
                "Очистите и промойте рыбу.",
                "Натрите солью и специями, дайте промариноваться 15 минут.",
                "Обжарьте на среднем огне по 5-7 минут с каждой стороны.",
                "Или запеките в духовке при 180°C 20-25 минут.",
                "Подавайте с лимоном и свежими овощами."
            ],
            "курица": [
                "Промойте курицу и обсушите бумажным полотенцем.",
                "Приправьте специями и солью.",
                "Обжарьте на сковороде до румяной корочки.",
                "Добавьте овощи или соус и тушите 25-30 минут.",
                "Проверьте готовность и подавайте горячим."
            ],
            "говядина": [
                "Нарежьте говядину кусочками среднего размера.",
                "Обжарьте мясо на сильном огне до корочки.",
                "Добавьте лук, морковь и специи.",
                "Тушите под крышкой 40-50 минут до мягкости.",
                "Подавайте с гарниром и свежими овощами."
            ],
            "свинина": [
                "Подготовьте свинину: промойте и нарежьте.",
                "Замаринуйте в специях на 20 минут.",
                "Обжарьте на среднем огне до румяности.",
                "Добавьте овощи и тушите 30 минут.",
                "Подавайте с любимым гарниром."
            ],
            "плов": [
                "Обжарьте мясо в казане до золотистой корочки.",
                "Добавьте лук и морковь, обжарьте 10 минут.",
                "Всыпьте промытый рис и залейте кипятком.",
                "Варите на малом огне 25-30 минут под крышкой.",
                "Дайте настояться 10 минут и подавайте."
            ],
            "паста": [
                "Отварите пасту в подсоленной воде до состояния аль денте.",
                "Приготовьте соус: обжарьте ингредиенты на сковороде.",
                "Слейте воду с пасты, оставив немного жидкости.",
                "Смешайте пасту с соусом и прогрейте минуту.",
                "Подавайте горячей, посыпав сыром и зеленью."
            ],
            "котлеты": [
                "Приготовьте фарш: смешайте мясо с луком и специями.",
                "Сформируйте котлеты влажными руками.",
                "Обваляйте в панировочных сухарях.",
                "Обжарьте на среднем огне по 5-7 минут с каждой стороны.",
                "Подавайте с картофельным пюре или овощами."
            ],
            "тефтели": [
                "Смешайте фарш с рисом, луком и специями.",
                "Сформируйте небольшие шарики.",
                "Обжарьте тефтели до румяной корочки.",
                "Залейте томатным соусом и тушите 20-25 минут.",
                "Подавайте со сметаной и зеленью."
            ],
            "запеканка": [
                "Подготовьте все ингредиенты и смешайте в форме.",
                "Добавьте яйца и молоко, перемешайте.",
                "Смажьте форму маслом и выложите смесь.",
                "Запекайте в духовке при 180°C 30-40 минут.",
                "Остудите немного и подавайте порционно."
            ],
            "блины": [
                "Смешайте яйца, молоко, муку и сахар до однородности.",
                "Дайте тесту постоять 15-20 минут.",
                "Разогрейте сковороду и смажьте маслом.",
                "Вылейте порцию теста и обжарьте с обеих сторон.",
                "Подавайте со сметаной, медом или вареньем."
            ],
            "оладьи": [
                "Замесите густое тесто из муки, яиц и кефира.",
                "Добавьте сахар и соду, перемешайте.",
                "Дайте тесту постоять 10 минут.",
                "Жарьте оладьи на среднем огне до румяности.",
                "Подавайте горячими с медом или сметаной."
            ],
            "азу": [
                "Нарежьте мясо соломкой и обжарьте до корочки.",
                "Добавьте лук и морковь, жарьте 5 минут.",
                "Положите помидоры и соленые огурцы.",
                "Тушите под крышкой 30-40 минут.",
                "Подавайте с отварным картофелем."
            ],
            "рагу": [
                "Нарежьте все овощи и мясо кубиками.",
                "Обжарьте мясо до румяности.",
                "Добавьте овощи и специи.",
                "Тушите под крышкой 40-50 минут до готовности.",
                "Подавайте горячим с хлебом."
            ],
            "default": [
                "Подготовьте все ингредиенты: промойте, очистите и нарежьте.",
                "Разогрейте сковороду или кастрюлю на среднем огне.",
                "Добавьте основные ингредиенты и готовьте согласно рецепту.",
                "Приправьте специями и доведите до готовности.",
                "Подавайте в теплом виде, украсив зеленью."
            ]
        }

        # Определяем тип блюда по названию
        dish_lower = dish_name.lower()
        instructions = None

        for keyword, template in cooking_templates.items():
            if keyword in dish_lower:
                instructions = template.copy()
                break

        if not instructions:
            instructions = cooking_templates["default"]

        return "\n".join([f"{i+1}. {step}" for i, step in enumerate(instructions)])

    def _improve_ingredients(self, ingredients_list, dish_name):
        """Улучшает список ингредиентов, заменяя 'по вкусу' на конкретные значения"""
        # База данных типичных количеств для разных ингредиентов
        typical_amounts = {
            "яйца": "2-3 шт",
            "яйцо": "2-3 шт",
            "молоко": "100 мл",
            "мука": "2-3 ст.л.",
            "сахар": "1 ч.л.",
            "соль": "по вкусу",
            "масло сливочное": "30 г",
            "масло растительное": "2 ст.л.",
            "перец": "щепотка",
            "сыр": "80-100 г",
            "помидоры": "2 шт",
            "огурцы": "1-2 шт",
            "лук": "1 шт",
            "морковь": "1 шт",
            "картофель": "3-4 шт",
            "мясо": "300 г",
            "курица": "400 г",
            "рыба": "300 г",
            "рис": "150 г",
            "гречка": "150 г",
            "макароны": "200 г",
            "зелень": "пучок",
            "чеснок": "2-3 зубчика",
            "сметана": "2-3 ст.л.",
            "майонез": "2 ст.л.",
            "вода": "500 мл",
            "бульон": "500 мл"
        }

        improved = []
        for ing in ingredients_list:
            # Разбираем ингредиент
            parts = ing.split("—")
            if len(parts) >= 2:
                name = parts[0].strip()
                amount = parts[1].strip()

                # Если количество "по вкусу", заменяем на типичное
                if "по вкусу" in amount.lower():
                    name_lower = name.lower()
                    # Ищем подходящее типичное количество
                    for key, typical_amt in typical_amounts.items():
                        if key in name_lower:
                            amount = typical_amt
                            break

                improved.append(f"{name} — {amount}")
            else:
                improved.append(ing)

        return improved

    def _convert_to_old_format(self, recipe):
        """Конвертация формата рецепта из book/"""
        # Парсим БЖУ из строки "35/28/12"
        bju = recipe.get("Конец. Б/Ж/У", "0/0/0").split("/")
        protein = int(bju[0]) if len(bju) > 0 else 20
        fats = int(bju[1]) if len(bju) > 1 else 15
        carbs = int(bju[2]) if len(bju) > 2 else 40

        # Название блюда
        dish_name = recipe.get("Название блюда", "Блюдо")

        # Ингредиенты - улучшаем их
        ingredients_list = recipe.get("Ингредиенты", [])
        improved_ingredients = self._improve_ingredients(ingredients_list, dish_name)

        ingredients_dict = {}
        for ing in improved_ingredients:
            # Парсим "Яйцо — 4 шт" -> {"яйцо": 4}
            parts = ing.split("—")
            if len(parts) >= 2:
                name = parts[0].strip().lower()
                ingredients_dict[name] = ing  # Сохраняем полную строку

        # Используем инструкции из JSON, если они есть
        cooking_instructions = recipe.get("Приготовление", "")

        # Если инструкций нет в JSON - генерируем
        if not cooking_instructions:
            cooking_instructions = self._generate_cooking_instructions(dish_name, improved_ingredients)

        return {
            "Название блюда": dish_name,
            "Ингредиенты": improved_ingredients,
            "Приготовление": cooking_instructions,
            "calories": int(recipe.get("Ккал", 400)),
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
            # Добавляем поля для совместимости со старым кодом
            "name_ru": dish_name,
            "name_en": dish_name,  # Будет переводиться позже
            "name_uz": dish_name,  # Будет переводиться позже
            "ingredients": ingredients_dict,  # Словарь для фильтрации
            "steps_ru": [cooking_instructions],
            "steps_en": [cooking_instructions],
            "steps_uz": [cooking_instructions],
        }

    def _create_default_recipe(self, meal_type):
        return {
            "Название блюда": f"Базовое блюдо ({meal_type})",
            "Ингредиенты": ["Основной ингредиент 200г"],
            "Приготовление": "Стандартная готовка",
            "calories": 400,
            "protein": 20,
            "carbs": 40,
            "fats": 15
        }

recipes_loader = RecipesLoader()
