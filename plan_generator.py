"""
Генератор HTML-планов питания для мини-приложения
"""
import os
import hashlib
from typing import Dict, List

def generate_html_plan(breakfast: Dict, lunch: Dict, dinner: Dict,
                       total_stats: Dict, metabolism: Dict, goal: str) -> str:
    """
    Генерирует HTML-план питания на основе шаблона

    Args:
        breakfast: Данные завтрака
        lunch: Данные обеда
        dinner: Данные ужина
        total_stats: Общая статистика (калории, БЖУ)
        metabolism: Данные метаболизма (BMR, TDEE)
        goal: Цель (lose_weight, gain_muscle, maintain)

    Returns:
        HTML-код плана питания
    """

    # Читаем шаблон
    template_path = os.path.join('templates', 'plan_style_colorful.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Функция для форматирования ингредиентов
    def format_ingredients(ingredients: List[str]) -> str:
        result = ""
        for ing in ingredients:
            # Разделяем название и количество
            parts = ing.split('—')
            if len(parts) == 2:
                name = parts[0].strip()
                amount = parts[1].strip()
            else:
                name = ing.strip()
                amount = "по вкусу"

            result += f'''
                    <div class="ingredient">
                        <span class="ingredient-bullet">•</span>
                        <span class="ingredient-name">{name}</span>
                        <span class="ingredient-amount">{amount}</span>
                    </div>'''
        return result

    # Заменяем данные завтрака
    html = html.replace('🍳 Пшенная каша с изюмом', f'🍳 {breakfast["Название блюда"]}')

    # Находим и заменяем ингредиенты завтрака
    breakfast_ingredients_start = html.find('<!-- ЗАВТРАК -->')
    breakfast_ingredients_section = html.find('<div class="ingredients-list">', breakfast_ingredients_start)
    breakfast_ingredients_end = html.find('</div>', breakfast_ingredients_section + len('<div class="ingredients-list">'))

    old_breakfast_ing = html[breakfast_ingredients_section:breakfast_ingredients_end + 6]
    new_breakfast_ing = f'<div class="ingredients-list">{format_ingredients(breakfast["Ингредиенты"])}\n                </div>'
    html = html.replace(old_breakfast_ing, new_breakfast_ing, 1)

    # Заменяем приготовление завтрака
    breakfast_cooking = breakfast.get('Приготовление', '')
    old_breakfast_cooking = 'Пшено тщательно промойте. Залейте молоком, добавьте соль и варите на медленном огне 25-30 минут. За 10 минут до готовности добавьте промытый изюм и сахар. В готовую кашу добавьте масло и мед. Хорошо перемешайте.'
    html = html.replace(old_breakfast_cooking, breakfast_cooking, 1)

    # Заменяем калории и БЖУ завтрака
    html = html.replace('🔥 625 ккал', f'🔥 {breakfast.get("calories", 0)} ккал', 1)
    html = html.replace('💪 22г', f'💪 {breakfast.get("protein", 0)}г', 1)
    html = html.replace('🥑 25г', f'🥑 {breakfast.get("fats", 0)}г', 1)
    html = html.replace('🍞 78г', f'🍞 {breakfast.get("carbs", 0)}г', 1)

    # Заменяем данные обеда
    html = html.replace('🍳 Картофель тушеный с грибами', f'🍳 {lunch["Название блюда"]}')

    # Находим и заменяем ингредиенты обеда
    lunch_ingredients_start = html.find('<!-- ОБЕД -->')
    lunch_ingredients_section = html.find('<div class="ingredients-list">', lunch_ingredients_start)
    lunch_ingredients_end = html.find('</div>', lunch_ingredients_section + len('<div class="ingredients-list">'))

    old_lunch_ing = html[lunch_ingredients_section:lunch_ingredients_end + 6]
    new_lunch_ing = f'<div class="ingredients-list">{format_ingredients(lunch["Ингредиенты"])}\n                </div>'
    html = html.replace(old_lunch_ing, new_lunch_ing, 1)

    # Заменяем приготовление обеда
    lunch_cooking = lunch.get('Приготовление', '')
    old_lunch_cooking = 'Картофель нарежьте кубиками. Обжарьте грибы с луком и морковью. Добавьте картофель, залейте водой. Тушите 30 минут. Добавьте сметану.'
    html = html.replace(old_lunch_cooking, lunch_cooking, 1)

    # Заменяем калории и БЖУ обеда
    html = html.replace('🔥 750 ккал', f'🔥 {lunch.get("calories", 0)} ккал', 1)
    html = html.replace('💪 25г', f'💪 {lunch.get("protein", 0)}г', 1)
    html = html.replace('🥑 30г', f'🥑 {lunch.get("fats", 0)}г', 1)
    html = html.replace('🍞 85г', f'🍞 {lunch.get("carbs", 0)}г', 1)

    # Заменяем данные ужина
    html = html.replace('🍳 Кабачковые рулетики с творогом', f'🍳 {dinner["Название блюда"]}')

    # Находим и заменяем ингредиенты ужина
    dinner_ingredients_start = html.find('<!-- УЖИН -->')
    dinner_ingredients_section = html.find('<div class="ingredients-list">', dinner_ingredients_start)
    dinner_ingredients_end = html.find('</div>', dinner_ingredients_section + len('<div class="ingredients-list">'))

    old_dinner_ing = html[dinner_ingredients_section:dinner_ingredients_end + 6]
    new_dinner_ing = f'<div class="ingredients-list">{format_ingredients(dinner["Ингредиенты"])}\n                </div>'
    html = html.replace(old_dinner_ing, new_dinner_ing, 1)

    # Заменяем приготовление ужина
    dinner_cooking = dinner.get('Приготовление', '')
    old_dinner_cooking = 'Кабачки нарежьте тонкими пластинами, обжарьте. Смешайте творог с чесноком и укропом. На каждую пластину кабачка выложите начинку, сверните рулетиком.'
    html = html.replace(old_dinner_cooking, dinner_cooking, 1)

    # Заменяем калории и БЖУ ужина
    html = html.replace('🔥 580 ккал', f'🔥 {dinner.get("calories", 0)} ккал', 1)
    html = html.replace('💪 35г', f'💪 {dinner.get("protein", 0)}г', 1)
    html = html.replace('🥑 25г', f'🥑 {dinner.get("fats", 0)}г', 1)
    html = html.replace('🍞 22г', f'🍞 {dinner.get("carbs", 0)}г', 1)

    # Заменяем итоговую статистику
    html = html.replace('<div class="stat-value">1955</div>', f'<div class="stat-value">{total_stats["calories"]}</div>')
    html = html.replace('цель: 2272 ккал', f'цель: {total_stats["target_calories"]} ккал')
    html = html.replace('<div class="stat-value">82г</div>', f'<div class="stat-value">{total_stats["protein"]}г</div>')
    html = html.replace('<div class="stat-value">80г</div>', f'<div class="stat-value">{total_stats["fats"]}г</div>')
    html = html.replace('<div class="stat-value">185г</div>', f'<div class="stat-value">{total_stats["carbs"]}г</div>')

    # Заменяем метаболизм
    html = html.replace('1273 ккал/день', f'{metabolism["bmr"]} ккал/день')
    html = html.replace('1973 ккал/день', f'{metabolism["tdee"]} ккал/день')

    # Заменяем прогноз
    goal_text = {
        'lose_weight': f'Прогноз похудения: -{abs(total_stats["weekly_change"]):.2f} кг/неделю',
        'gain_muscle': f'Прогноз набора: +{abs(total_stats["weekly_change"]):.2f} кг/неделю',
        'maintain': 'Прогноз: поддержание веса'
    }

    html = html.replace('Прогноз набора:</strong> +0.02 кг/неделю', goal_text.get(goal, 'Прогноз: поддержание веса'))

    return html


def save_plan_html(html: str, user_id: int) -> str:
    """
    Сохраняет HTML-план в файл

    Args:
        html: HTML-код плана
        user_id: ID пользователя

    Returns:
        Путь к сохраненному файлу
    """
    # Создаем папку для планов если её нет
    plans_dir = os.path.join('static', 'plans')
    os.makedirs(plans_dir, exist_ok=True)

    # Генерируем уникальное имя файла
    timestamp = str(int(os.time.time() if hasattr(os, 'time') else 0))
    filename = f'plan_{user_id}_{timestamp}.html'
    filepath = os.path.join(plans_dir, filename)

    # Сохраняем
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath
