"""
КАЛЬКУЛЯТОР КБЖУ
Расчет дневной нормы калорий, белков, жиров, углеводов
"""

from typing import Dict, Tuple


class CaloriesCalculator:
    """Калькулятор калорий и макронутриентов"""

    # Коэффициенты активности
    ACTIVITY_LEVELS = {
        'sedentary': 1.2,      # Сидячий образ жизни
        'light': 1.375,        # Легкая активность (1-3 дня/неделю)
        'moderate': 1.55,      # Умеренная (3-5 дней/неделю)
        'active': 1.725,       # Высокая (6-7 дней/неделю)
        'very_active': 1.9     # Очень высокая (2 раза в день)
    }

    def __init__(self):
        pass

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """
        Расчет базального метаболизма (BMR) по формуле Миффлина-Сан Жеора

        Args:
            weight: Вес в кг
            height: Рост в см
            age: Возраст в годах
            gender: Пол ('male' или 'female')

        Returns:
            BMR (ккал/день)
        """

        if gender.lower() in ['male', 'm', 'мужской', 'м']:
            # Для мужчин
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            # Для женщин
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        return bmr

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Расчет общего расхода энергии (TDEE)

        Args:
            bmr: Базальный метаболизм
            activity_level: Уровень активности

        Returns:
            TDEE (ккал/день)
        """

        coefficient = self.ACTIVITY_LEVELS.get(activity_level, 1.55)
        return bmr * coefficient

    def calculate_daily_calories(self, weight: float, height: float, age: int,
                                 gender: str, activity_level: str, goal: str) -> int:
        """
        Расчет дневной нормы калорий с учетом цели

        Args:
            weight: Вес в кг
            height: Рост в см
            age: Возраст
            gender: Пол
            activity_level: Уровень активности
            goal: Цель (lose_weight, gain_weight, maintain_weight)

        Returns:
            Дневная норма калорий
        """

        # Рассчитываем BMR
        bmr = self.calculate_bmr(weight, height, age, gender)

        # Рассчитываем TDEE
        tdee = self.calculate_tdee(bmr, activity_level)

        # Корректируем по цели
        if goal == 'lose_weight':
            # Дефицит 20% для похудения
            daily_calories = tdee * 0.8
        elif goal == 'gain_weight':
            # Профицит 15% для набора массы
            daily_calories = tdee * 1.15
        else:
            # Maintain_weight - без изменений
            daily_calories = tdee

        return int(daily_calories)

    def calculate_macros(self, daily_calories: int, goal: str) -> Dict[str, int]:
        """
        Расчет макронутриентов (БЖУ)

        Args:
            daily_calories: Дневная норма калорий
            goal: Цель

        Returns:
            {'protein': int, 'fats': int, 'carbs': int}
        """

        if goal == 'lose_weight':
            # Похудение: больше белка, меньше углеводов
            # Белки: 40%, Жиры: 30%, Углеводы: 30%
            protein_percent = 0.40
            fats_percent = 0.30
            carbs_percent = 0.30

        elif goal == 'gain_weight':
            # Набор массы: больше белка и углеводов
            # Белки: 30%, Жиры: 20%, Углеводы: 50%
            protein_percent = 0.30
            fats_percent = 0.20
            carbs_percent = 0.50

        else:
            # Поддержание: сбалансированно
            # Белки: 30%, Жиры: 30%, Углеводы: 40%
            protein_percent = 0.30
            fats_percent = 0.30
            carbs_percent = 0.40

        # Калории из макронутриентов:
        # 1г белка = 4 ккал
        # 1г жира = 9 ккал
        # 1г углеводов = 4 ккал

        protein_calories = daily_calories * protein_percent
        fats_calories = daily_calories * fats_percent
        carbs_calories = daily_calories * carbs_percent

        protein_grams = int(protein_calories / 4)
        fats_grams = int(fats_calories / 9)
        carbs_grams = int(carbs_calories / 4)

        return {
            'protein': protein_grams,
            'fats': fats_grams,
            'carbs': carbs_grams
        }

    def get_full_recommendation(self, weight: float, height: float, age: int,
                               gender: str, activity_level: str, goal: str) -> Dict:
        """
        Полная рекомендация по питанию

        Returns:
            {
                'bmr': int,
                'tdee': int,
                'daily_calories': int,
                'protein': int,
                'fats': int,
                'carbs': int,
                'meals': {
                    'breakfast': int,
                    'lunch': int,
                    'dinner': int,
                    'snacks': int
                }
            }
        """

        bmr = self.calculate_bmr(weight, height, age, gender)
        tdee = self.calculate_tdee(bmr, activity_level)
        daily_calories = self.calculate_daily_calories(
            weight, height, age, gender, activity_level, goal
        )
        macros = self.calculate_macros(daily_calories, goal)

        # Распределение калорий по приемам пищи
        # Завтрак: 30%, Обед: 40%, Ужин: 25%, Перекусы: 5%
        meals = {
            'breakfast': int(daily_calories * 0.30),
            'lunch': int(daily_calories * 0.40),
            'dinner': int(daily_calories * 0.25),
            'snacks': int(daily_calories * 0.05)
        }

        return {
            'bmr': int(bmr),
            'tdee': int(tdee),
            'daily_calories': daily_calories,
            'protein': macros['protein'],
            'fats': macros['fats'],
            'carbs': macros['carbs'],
            'meals': meals,
            'goal': goal,
            'activity_level': activity_level
        }

    def adjust_for_training(self, base_calories: int, workout_calories: int,
                           goal: str) -> int:
        """
        Корректировка калорий с учетом тренировки

        Args:
            base_calories: Базовая норма калорий
            workout_calories: Калории сожженные на тренировке
            goal: Цель

        Returns:
            Скорректированная норма калорий
        """

        if goal == 'lose_weight':
            # При похудении не компенсируем все сожженные калории
            # Добавляем только 30%
            return base_calories + int(workout_calories * 0.3)

        elif goal == 'gain_weight':
            # При наборе массы компенсируем полностью + немного больше
            return base_calories + int(workout_calories * 1.1)

        else:
            # При поддержании компенсируем полностью
            return base_calories + workout_calories

    def calculate_weight_change_prediction(self, daily_deficit: int, weeks: int) -> Dict:
        """
        Прогноз изменения веса

        Args:
            daily_deficit: Дефицит/профицит калорий в день
            weeks: Количество недель

        Returns:
            {
                'total_deficit': int,
                'weight_change_kg': float,
                'weight_change_per_week': float
            }
        """

        # 1 кг жира = ~7700 ккал
        CALORIES_PER_KG = 7700

        total_deficit = daily_deficit * 7 * weeks
        weight_change = total_deficit / CALORIES_PER_KG
        weight_per_week = weight_change / weeks if weeks > 0 else 0

        return {
            'total_deficit': total_deficit,
            'weight_change_kg': round(weight_change, 1),
            'weight_change_per_week': round(weight_per_week, 2)
        }


# Создаем глобальный экземпляр
calories_calculator = CaloriesCalculator()


if __name__ == "__main__":
    # Тесты калькулятора

    print("=" * 80)
    print("ТЕСТ КАЛЬКУЛЯТОРА КБЖУ")
    print("=" * 80)

    # Тестовый пользователь 1: Женщина, похудение
    print("\nПРИМЕР 1: Женщина, 25 лет, 70кг, 165см, умеренная активность, ПОХУДЕНИЕ")
    result = calories_calculator.get_full_recommendation(
        weight=70,
        height=165,
        age=25,
        gender='female',
        activity_level='moderate',
        goal='lose_weight'
    )

    print(f"BMR (базовый метаболизм): {result['bmr']} ккал")
    print(f"TDEE (общий расход): {result['tdee']} ккал")
    print(f"Дневная норма: {result['daily_calories']} ккал")
    print(f"\nМакронутриенты:")
    print(f"  Белки: {result['protein']}г")
    print(f"  Жиры: {result['fats']}г")
    print(f"  Углеводы: {result['carbs']}г")
    print(f"\nРаспределение по приемам пищи:")
    for meal, cals in result['meals'].items():
        print(f"  {meal}: {cals} ккал")

    # Прогноз похудения
    deficit = result['tdee'] - result['daily_calories']
    prediction = calories_calculator.calculate_weight_change_prediction(deficit, 8)
    print(f"\nПрогноз за 8 недель:")
    print(f"  Изменение веса: {prediction['weight_change_kg']} кг")
    print(f"  В неделю: {prediction['weight_change_per_week']} кг")

    # Тестовый пользователь 2: Мужчина, набор массы
    print("\n" + "=" * 80)
    print("ПРИМЕР 2: Мужчина, 22 года, 75кг, 180см, высокая активность, НАБОР МАССЫ")
    result = calories_calculator.get_full_recommendation(
        weight=75,
        height=180,
        age=22,
        gender='male',
        activity_level='active',
        goal='gain_weight'
    )

    print(f"BMR: {result['bmr']} ккал")
    print(f"TDEE: {result['tdee']} ккал")
    print(f"Дневная норма: {result['daily_calories']} ккал")
    print(f"\nМакронутриенты:")
    print(f"  Белки: {result['protein']}г ({result['protein'] / 75:.1f}г на кг веса)")
    print(f"  Жиры: {result['fats']}г")
    print(f"  Углеводы: {result['carbs']}г")

    surplus = result['daily_calories'] - result['tdee']
    prediction = calories_calculator.calculate_weight_change_prediction(surplus, 12)
    print(f"\nПрогноз за 12 недель:")
    print(f"  Прибавка веса: +{prediction['weight_change_kg']} кг")
    print(f"  В неделю: +{prediction['weight_change_per_week']} кг")

    # Тест с тренировкой
    print("\n" + "=" * 80)
    print("ПРИМЕР 3: Корректировка калорий после тренировки")

    workout_calories = 400
    base_calories = 2000

    for goal in ['lose_weight', 'gain_weight', 'maintain_weight']:
        adjusted = calories_calculator.adjust_for_training(
            base_calories, workout_calories, goal
        )
        print(f"\n{goal}:")
        print(f"  База: {base_calories} ккал")
        print(f"  Сожжено: {workout_calories} ккал")
        print(f"  Скорректировано: {adjusted} ккал")
        print(f"  Разница: {adjusted - base_calories:+d} ккал")

    print("\n" + "=" * 80)
    print("[OK] Калькулятор работает!")
    print("=" * 80)
