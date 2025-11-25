"""
ФИЛЬТР ПИТАНИЯ ПО АЛЛЕРГИЯМ И ПРЕДПОЧТЕНИЯМ
Исключает рецепты с запрещенными продуктами
"""

from recipes_loader import recipes_loader
from typing import List, Dict, Set


class FoodFilter:
    """Фильтрация рецептов по предпочтениям"""

    # Продукты с лактозой
    LACTOSE_PRODUCTS = [
        'молоко', 'сливки', 'сметана', 'кефир', 'йогурт', 'творог',
        'сыр', 'масло сливочное', 'мороженое', 'сгущенка'
    ]

    # Продукты с глютеном
    GLUTEN_PRODUCTS = [
        'пшеница', 'мука', 'хлеб', 'макароны', 'манка', 'булка',
        'печенье', 'торт', 'овсянка', 'ячмень', 'рожь'
    ]

    # Мясо
    MEAT_PRODUCTS = [
        'говядина', 'свинина', 'баранина', 'мясо', 'фарш', 'колбаса',
        'сосиски', 'курица', 'индейка', 'утка', 'кролик'
    ]

    # Рыба и морепродукты
    FISH_PRODUCTS = [
        'рыба', 'треска', 'лосось', 'тунец', 'семга', 'форель',
        'креветки', 'кальмар', 'мидии', 'краб'
    ]

    # Яйца
    EGG_PRODUCTS = ['яйцо', 'яичный', 'омлет']

    # Орехи
    NUT_PRODUCTS = [
        'орех', 'грецкий', 'миндаль', 'кешью', 'фундук',
        'арахис', 'фисташки'
    ]

    CATEGORY_MAP = {
        'лактоза': LACTOSE_PRODUCTS,
        'lactose': LACTOSE_PRODUCTS,
        'глютен': GLUTEN_PRODUCTS,
        'gluten': GLUTEN_PRODUCTS,
        'мясо': MEAT_PRODUCTS,
        'meat': MEAT_PRODUCTS,
        'рыба': FISH_PRODUCTS,
        'fish': FISH_PRODUCTS,
        'яйца': EGG_PRODUCTS,
        'eggs': EGG_PRODUCTS,
        'орехи': NUT_PRODUCTS,
        'nuts': NUT_PRODUCTS,
    }

    def __init__(self):
        self.recipes_loader = recipes_loader

    def filter_recipes(self, goal: str, meal_type: str,
                      allergies: List[str] = None,
                      excluded_foods: List[str] = None,
                      diet_type: str = None,
                      count: int = 10) -> List[Dict]:
        """
        Фильтрация рецептов

        Args:
            goal: Цель (lose_weight, gain_weight, maintain_weight)
            meal_type: Тип еды (breakfast, lunch, dinner)
            allergies: Список аллергий ['лактоза', 'глютен', 'орехи']
            excluded_foods: Список исключенных продуктов ['свинина', 'грибы']
            diet_type: Тип диеты (vegetarian, vegan, pescatarian)
            count: Количество рецептов

        Returns:
            Список отфильтрованных рецептов
        """

        # Получаем все рецепты
        all_recipes = self.recipes_loader.recipes.get(meal_type, [])

        if not all_recipes:
            return []

        # Собираем все запрещенные продукты
        forbidden = set()

        # Добавляем из аллергий
        if allergies:
            for allergy in allergies:
                allergy_lower = allergy.lower()
                if allergy_lower in self.CATEGORY_MAP:
                    forbidden.update(self.CATEGORY_MAP[allergy_lower])

        # Добавляем исключенные продукты
        if excluded_foods:
            forbidden.update([food.lower() for food in excluded_foods])

        # Добавляем по типу диеты
        if diet_type:
            if diet_type in ['vegetarian', 'вегетарианство']:
                forbidden.update(self.MEAT_PRODUCTS)
                forbidden.update(self.FISH_PRODUCTS)
            elif diet_type in ['vegan', 'веганство']:
                forbidden.update(self.MEAT_PRODUCTS)
                forbidden.update(self.FISH_PRODUCTS)
                forbidden.update(self.EGG_PRODUCTS)
                forbidden.update(self.LACTOSE_PRODUCTS)
            elif diet_type in ['pescatarian', 'пескетарианство']:
                forbidden.update(self.MEAT_PRODUCTS)

        # Фильтруем рецепты
        filtered = []

        for recipe in all_recipes:
            if self._is_recipe_allowed(recipe, forbidden):
                filtered.append(recipe)

        # Возвращаем случайные из отфильтрованных
        if filtered:
            import random
            return random.sample(filtered, min(count, len(filtered)))

        return []

    def _is_recipe_allowed(self, recipe: Dict, forbidden: Set[str]) -> bool:
        """Проверить, можно ли использовать рецепт"""

        if not forbidden:
            return True

        # Проверяем ингредиенты
        ingredients = recipe.get('Ингредиенты', [])

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()

            # Проверяем каждый запрещенный продукт
            for forbidden_food in forbidden:
                if forbidden_food in ingredient_lower:
                    return False

        return True

    def get_filtered_recipe(self, goal: str, meal_type: str,
                           allergies: List[str] = None,
                           excluded_foods: List[str] = None,
                           diet_type: str = None) -> Dict:
        """Получить один отфильтрованный рецепт"""

        recipes = self.filter_recipes(goal, meal_type, allergies,
                                      excluded_foods, diet_type, count=1)

        if recipes:
            return recipes[0]

        # Если ничего не найдено, возвращаем дефолтный
        return {
            'Название блюда': 'Базовое блюдо',
            'Ингредиенты': ['Продукты по выбору'],
            'Приготовление': 'Приготовить по стандартному рецепту',
            'calories': 400,
            'protein': 20,
            'fats': 15,
            'carbs': 40
        }

    def check_recipe_compatibility(self, recipe: Dict,
                                   allergies: List[str] = None,
                                   excluded_foods: List[str] = None) -> Dict:
        """
        Проверить совместимость рецепта с предпочтениями

        Returns:
            {
                'compatible': bool,
                'issues': List[str],  # Список проблем
                'warnings': List[str]  # Предупреждения
            }
        """

        result = {
            'compatible': True,
            'issues': [],
            'warnings': []
        }

        forbidden = set()

        if allergies:
            for allergy in allergies:
                allergy_lower = allergy.lower()
                if allergy_lower in self.CATEGORY_MAP:
                    forbidden.update(self.CATEGORY_MAP[allergy_lower])

        if excluded_foods:
            forbidden.update([food.lower() for food in excluded_foods])

        ingredients = recipe.get('Ингредиенты', [])

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()

            for forbidden_food in forbidden:
                if forbidden_food in ingredient_lower:
                    result['compatible'] = False
                    result['issues'].append(
                        f"Содержит '{forbidden_food}' в ингредиенте: {ingredient}"
                    )

        return result


# Создаем глобальный экземпляр
food_filter = FoodFilter()


if __name__ == "__main__":
    # Тесты фильтра

    print("ТЕСТ 1: Фильтр без ограничений")
    recipes = food_filter.filter_recipes('lose_weight', 'breakfast', count=5)
    print(f"Найдено рецептов: {len(recipes)}")
    for r in recipes:
        print(f"  - {r['Название блюда']}")

    print("\nТЕСТ 2: Исключение лактозы")
    recipes = food_filter.filter_recipes(
        'lose_weight', 'breakfast',
        allergies=['лактоза'],
        count=5
    )
    print(f"Найдено рецептов без лактозы: {len(recipes)}")
    for r in recipes:
        print(f"  - {r['Название блюда']}")
        print(f"    Ингредиенты: {', '.join(r['Ингредиенты'][:3])}")

    print("\nТЕСТ 3: Вегетарианство")
    recipes = food_filter.filter_recipes(
        'gain_weight', 'lunch',
        diet_type='vegetarian',
        count=5
    )
    print(f"Вегетарианских рецептов: {len(recipes)}")
    for r in recipes:
        print(f"  - {r['Название блюда']}")

    print("\nТЕСТ 4: Веганство (без мяса, рыбы, яиц, молока)")
    recipes = food_filter.filter_recipes(
        'maintain_weight', 'dinner',
        diet_type='vegan',
        count=5
    )
    print(f"Веганских рецептов: {len(recipes)}")
    for r in recipes:
        print(f"  - {r['Название блюда']}")

    print("\nТЕСТ 5: Несколько исключений")
    recipes = food_filter.filter_recipes(
        'lose_weight', 'lunch',
        allergies=['глютен', 'лактоза'],
        excluded_foods=['свинина', 'грибы'],
        count=3
    )
    print(f"Рецептов с учетом всех ограничений: {len(recipes)}")
    for r in recipes:
        print(f"  - {r['Название блюда']}")

    print("\nТЕСТ 6: Проверка совместимости")
    recipe = recipes_loader.get_recipe('gain_weight', 'breakfast')
    compat = food_filter.check_recipe_compatibility(
        recipe,
        allergies=['лактоза']
    )
    print(f"Рецепт: {recipe['Название блюда']}")
    print(f"Совместимость: {compat['compatible']}")
    if compat['issues']:
        print(f"Проблемы: {compat['issues']}")

    print("\n[OK] Фильтр работает!")
