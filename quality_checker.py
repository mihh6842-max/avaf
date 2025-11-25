"""
Система проверки качества сгенерированных планов
Проверяет корректность, точность и качество
"""

import re
from typing import Dict, List


class QualityChecker:
    """Проверяет качество сгенерированных планов"""

    @staticmethod
    def verify_nutrition_plan(plan_text: str, language: str, target_calories: int) -> dict:
        """
        Проверяет план питания на корректность

        Returns:
            {
                'valid': bool,
                'errors': list,
                'warnings': list,
                'score': int (0-100)
            }
        """
        errors = []
        warnings = []
        score = 100

        # Проверка 1: Язык
        if not QualityChecker._check_language_purity(plan_text, language):
            errors.append(f"Обнаружено смешивание языков (ожидался {language})")
            score -= 30

        # Проверка 2: Калории
        parsed_calories = QualityChecker._parse_calories_from_text(plan_text)
        if parsed_calories:
            calorie_diff = abs(parsed_calories - target_calories)
            if calorie_diff > 200:
                errors.append(f"Калории сильно не сходятся: {parsed_calories} vs {target_calories} (разница {calorie_diff})")
                score -= 25
            elif calorie_diff > 100:
                warnings.append(f"Калории немного не сходятся: {parsed_calories} vs {target_calories} (разница {calorie_diff})")
                score -= 10

        # Проверка 3: Структура
        required_sections = QualityChecker._get_required_sections(language)
        missing_sections = []
        for section_name, section_marker in required_sections.items():
            if section_marker not in plan_text:
                missing_sections.append(section_name)
                score -= 10

        if missing_sections:
            errors.append(f"Отсутствуют секции: {', '.join(missing_sections)}")

        # Проверка 4: Наличие ингредиентов
        if not QualityChecker._has_ingredients(plan_text):
            errors.append("В плане отсутствуют ингредиенты")
            score -= 15

        # Проверка 5: Наличие шагов приготовления
        if not QualityChecker._has_cooking_steps(plan_text):
            warnings.append("В плане могут отсутствовать шаги приготовления")
            score -= 5

        # Проверка 6: Макронутриенты
        macros = QualityChecker._parse_macros_from_text(plan_text)
        if macros:
            macro_warnings = QualityChecker._validate_macros(macros, target_calories)
            warnings.extend(macro_warnings)
            score -= len(macro_warnings) * 5

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': max(0, score)
        }

    @staticmethod
    def verify_workout_plan(plan_text: str, language: str) -> dict:
        """
        Проверяет план тренировки на корректность

        Returns:
            {
                'valid': bool,
                'errors': list,
                'warnings': list,
                'score': int (0-100)
            }
        """
        errors = []
        warnings = []
        score = 100

        # Проверка 1: Язык
        if not QualityChecker._check_language_purity(plan_text, language):
            errors.append(f"Обнаружено смешивание языков (ожидался {language})")
            score -= 30

        # Проверка 2: Наличие упражнений
        exercise_count = QualityChecker._count_exercises(plan_text)
        if exercise_count == 0:
            errors.append("В плане нет упражнений")
            score -= 40
        elif exercise_count < 3:
            warnings.append(f"Мало упражнений в плане: {exercise_count}")
            score -= 10

        # Проверка 3: Наличие подходов/повторений
        if not QualityChecker._has_sets_and_reps(plan_text):
            warnings.append("Возможно отсутствует информация о подходах и повторениях")
            score -= 15

        # Проверка 4: Наличие техники выполнения
        if not QualityChecker._has_technique_info(plan_text, language):
            warnings.append("Отсутствует описание техники выполнения")
            score -= 10

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': max(0, score)
        }

    @staticmethod
    def _check_language_purity(text: str, expected_lang: str) -> bool:
        """Проверяет чистоту языка"""

        if expected_lang == 'ru':
            # Не должно быть длинных английских слов (кроме BMR, TDEE)
            english_words = re.findall(r'\b[A-Za-z]{5,}\b', text)
            # Исключаем допустимые термины
            allowed_terms = ['BMR', 'TDEE']
            english_words = [w for w in english_words if w.upper() not in allowed_terms]
            return len(english_words) < 3  # Допускаем до 3 английских слов

        elif expected_lang == 'en':
            # Не должно быть кириллицы
            cyrillic_count = len(re.findall(r'[А-Яа-яЁё]', text))
            return cyrillic_count == 0

        elif expected_lang == 'uz':
            # Не должно быть кириллицы (узбекский на латинице)
            cyrillic_count = len(re.findall(r'[А-Яа-яЁё]', text))
            return cyrillic_count == 0

        return True

    @staticmethod
    def _parse_calories_from_text(text: str) -> int:
        """Парсит общую калорийность из текста"""

        # Ищем строку типа "Итого в плане: 2000 ккал"
        patterns = [
            r'[Ии]того в плане[:\s]+(\d+)\s*(?:ккал|kcal|kkal)',
            r'[Tt]otal in plan[:\s]+(\d+)\s*(?:ккал|kcal|kkal)',
            r'[Rr]ejada jami[:\s]+(\d+)\s*(?:ккал|kcal|kkal)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 0

    @staticmethod
    def _parse_macros_from_text(text: str) -> Dict[str, float]:
        """Парсит макронутриенты из текста"""

        macros = {'protein': 0, 'fat': 0, 'carbs': 0}

        # Паттерны для поиска макросов
        protein_patterns = [
            r'[Бб]елк[иа][:\s]+(\d+\.?\d*)\s*г',
            r'[Pp]rotein[:\s]+(\d+\.?\d*)\s*g',
            r'[Oo]qsil[:\s]+(\d+\.?\d*)\s*g'
        ]

        fat_patterns = [
            r'[Жж]ир[ыа][:\s]+(\d+\.?\d*)\s*г',
            r'[Ff]at[:\s]+(\d+\.?\d*)\s*g',
            r"[Yy]og'[:\s]+(\d+\.?\d*)\s*g"
        ]

        carbs_patterns = [
            r'[Уу]глевод[ыа][:\s]+(\d+\.?\d*)\s*г',
            r'[Cc]arbs[:\s]+(\d+\.?\d*)\s*g',
            r'[Uu]glevodlar[:\s]+(\d+\.?\d*)\s*g'
        ]

        # Суммируем все значения белков
        for pattern in protein_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            macros['protein'] += sum(float(m) for m in matches)

        # Суммируем все значения жиров
        for pattern in fat_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            macros['fat'] += sum(float(m) for m in matches)

        # Суммируем все значения углеводов
        for pattern in carbs_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            macros['carbs'] += sum(float(m) for m in matches)

        return macros if any(macros.values()) else None

    @staticmethod
    def _validate_macros(macros: Dict[str, float], target_calories: int) -> List[str]:
        """Проверяет корректность макронутриентов"""

        warnings = []

        # Рассчитываем калории из макросов
        calculated_calories = (macros['protein'] * 4) + (macros['fat'] * 9) + (macros['carbs'] * 4)

        # Проверяем соответствие
        if abs(calculated_calories - target_calories) > 200:
            warnings.append(
                f"Калории из макросов ({calculated_calories:.0f}) не соответствуют целевым ({target_calories})"
            )

        # Проверяем баланс макросов
        total_macro_grams = macros['protein'] + macros['fat'] + macros['carbs']
        if total_macro_grams > 0:
            protein_percent = (macros['protein'] * 4 / calculated_calories) * 100 if calculated_calories > 0 else 0
            fat_percent = (macros['fat'] * 9 / calculated_calories) * 100 if calculated_calories > 0 else 0
            carbs_percent = (macros['carbs'] * 4 / calculated_calories) * 100 if calculated_calories > 0 else 0

            # Проверяем разумность процентов
            if protein_percent < 15:
                warnings.append(f"Слишком мало белка: {protein_percent:.0f}% от калорий")
            elif protein_percent > 40:
                warnings.append(f"Слишком много белка: {protein_percent:.0f}% от калорий")

            if fat_percent < 15:
                warnings.append(f"Слишком мало жиров: {fat_percent:.0f}% от калорий")
            elif fat_percent > 40:
                warnings.append(f"Слишком много жиров: {fat_percent:.0f}% от калорий")

        return warnings

    @staticmethod
    def _get_required_sections(language: str) -> Dict[str, str]:
        """Возвращает обязательные секции в зависимости от языка"""

        if language == 'ru':
            return {
                'Завтрак': '🌅',
                'Обед': '🍽',
                'Ужин': '🌙',
                'Питательная ценность': '📊',
                'Совет': '💡'
            }
        elif language == 'en':
            return {
                'Breakfast': '🌅',
                'Lunch': '🍽',
                'Dinner': '🌙',
                'Nutritional value': '📊',
                'Tip': '💡'
            }
        elif language == 'uz':
            return {
                'Nonushta': '🌅',
                'Tushlik': '🍽',
                'Kechki ovqat': '🌙',
                'Ozuqaviy qiymat': '📊',
                'Maslahat': '💡'
            }
        else:
            return {}

    @staticmethod
    def _has_ingredients(text: str) -> bool:
        """Проверяет наличие списка ингредиентов"""

        ingredient_markers = [
            r'🛒.*[Ии]нгредиент',
            r'🛒.*[Ii]ngredient',
            r'🛒.*[Ii]ngredient',
            r'•.*—.*г',  # Маркер списка ингредиентов
            r'•.*—.*g'
        ]

        for pattern in ingredient_markers:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def _has_cooking_steps(text: str) -> bool:
        """Проверяет наличие шагов приготовления"""

        cooking_markers = [
            r'👨‍🍳.*[Пп]риготовление',
            r'👨‍🍳.*[Pp]reparation',
            r'👨‍🍳.*[Tt]ayyorlash',
            r'\d+\.\s+[А-ЯЁA-Z]',  # Нумерованные шаги
        ]

        for pattern in cooking_markers:
            if re.search(pattern, text):
                return True

        return False

    @staticmethod
    def _count_exercises(text: str) -> int:
        """Подсчитывает количество упражнений в плане"""

        # Ищем разделители упражнений
        exercise_separators = re.findall(r'─+', text)

        # Или ищем нумерованные упражнения
        numbered_exercises = re.findall(r'^\d+\.\s+[А-ЯЁA-Z]', text, re.MULTILINE)

        return max(len(exercise_separators) - 1, len(numbered_exercises))

    @staticmethod
    def _has_sets_and_reps(text: str) -> bool:
        """Проверяет наличие информации о подходах и повторениях"""

        sets_patterns = [
            r'[Пп]одход[ыа]',
            r'[Ss]ets',
            r'[Ss]etlar'
        ]

        reps_patterns = [
            r'[Пп]овторени[яй]',
            r'[Rr]eps',
            r'[Tt]akrorlar'
        ]

        has_sets = any(re.search(pattern, text, re.IGNORECASE) for pattern in sets_patterns)
        has_reps = any(re.search(pattern, text, re.IGNORECASE) for pattern in reps_patterns)

        return has_sets or has_reps

    @staticmethod
    def _has_technique_info(text: str, language: str) -> bool:
        """Проверяет наличие описания техники"""

        technique_markers = {
            'ru': [r'[Тт]ехник[аи]', r'✅'],
            'en': [r'[Tt]echnique', r'✅'],
            'uz': [r'[Tt]exnika', r'✅']
        }

        markers = technique_markers.get(language, technique_markers['ru'])

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in markers)

    @staticmethod
    def generate_report(verification_result: dict) -> str:
        """Генерирует читаемый отчёт о проверке"""

        lines = []
        lines.append("=" * 50)
        lines.append("ОТЧЁТ О ПРОВЕРКЕ КАЧЕСТВА")
        lines.append("=" * 50)
        lines.append("")

        # Статус
        status = "✅ УСПЕШНО" if verification_result['valid'] else "❌ ОШИБКИ"
        lines.append(f"Статус: {status}")
        lines.append(f"Оценка: {verification_result['score']}/100")
        lines.append("")

        # Ошибки
        if verification_result['errors']:
            lines.append("ОШИБКИ:")
            for error in verification_result['errors']:
                lines.append(f"  ❌ {error}")
            lines.append("")

        # Предупреждения
        if verification_result['warnings']:
            lines.append("ПРЕДУПРЕЖДЕНИЯ:")
            for warning in verification_result['warnings']:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")

        lines.append("=" * 50)

        return "\n".join(lines)
