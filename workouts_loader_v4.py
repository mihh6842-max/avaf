"""
ЗАГРУЗЧИК ТРЕНИРОВОК V4
Работает с новой структурой: уровень -> место -> цель_тип.json
"""

import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class WorkoutsLoaderV4:
    """
    Загрузчик тренировок V4 с новой структурой по уровням
    """

    # Калории в минуту для разных типов тренировок
    CALORIES_PER_MINUTE = {
        'strength': 6,
        'cardio': 10,
        'flexibility': 3,
        'full_body': 8
    }

    # Рекомендации по подходам и повторениям
    WORKOUT_RECOMMENDATIONS = {
        'lose_weight': {
            'strength': {'sets': '3-4', 'reps': '12-15', 'rest': '30-45 сек'},
            'cardio': {'sets': '1', 'reps': 'непрерывно', 'rest': 'минимальный'},
            'flexibility': {'sets': '2-3', 'reps': '30-60 сек', 'rest': '15-30 сек'},
            'full_body': {'sets': '3-4', 'reps': '15-20', 'rest': '30 сек'}
        },
        'gain_weight': {
            'strength': {'sets': '4-5', 'reps': '6-10', 'rest': '90-120 сек'},
            'cardio': {'sets': '1', 'reps': 'умеренно', 'rest': 'минимальный'},
            'flexibility': {'sets': '2', 'reps': '20-30 сек', 'rest': '15-30 сек'},
            'full_body': {'sets': '3-4', 'reps': '8-12', 'rest': '60-90 сек'}
        },
        'maintain_weight': {
            'strength': {'sets': '3-4', 'reps': '10-12', 'rest': '60-90 сек'},
            'cardio': {'sets': '1', 'reps': 'умеренно', 'rest': 'минимальный'},
            'flexibility': {'sets': '2-3', 'reps': '30-45 сек', 'rest': '15-30 сек'},
            'full_body': {'sets': '3-4', 'reps': '12-15', 'rest': '45-60 сек'}
        }
    }

    def __init__(self) -> None:
        self.workouts: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = self._load_workouts()
        self.used_exercises: Dict[str, List[str]] = {}  # История использованных упражнений
        self.workout_history_file = "workout_history.json"  # Файл для истории тренировок
        self._init_workout_history()

    def _init_workout_history(self):
        """Инициализация файла истории тренировок"""
        if not os.path.exists(self.workout_history_file):
            with open(self.workout_history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _load_workout_history(self, user_id: int) -> Dict:
        """Загрузить историю тренировок пользователя"""
        try:
            with open(self.workout_history_file, 'r', encoding='utf-8') as f:
                all_history = json.load(f)
            return all_history.get(str(user_id), {'workouts': [], 'exercises': {}})
        except Exception as e:
            print(f"[ERROR] Error loading workout history: {e}")
            return {'workouts': [], 'exercises': {}}

    def _load_workouts(self) -> Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]]:
        """Загрузка тренировок из новой структуры"""
        workouts = {}
        workouts_path = "book/workouts_by_level"

        try:
            # Уровни подготовки
            for level in ['beginner', 'intermediate', 'advanced']:
                workouts[level] = {}
                level_path = os.path.join(workouts_path, level)

                if not os.path.exists(level_path):
                    print(f"[WARNING] Level path not found: {level_path}")
                    continue

                # Места
                for location in ['home', 'gym', 'both']:
                    workouts[level][location] = {}
                    location_path = os.path.join(level_path, location)

                    if not os.path.exists(location_path):
                        continue

                    # Ищем все JSON файлы
                    try:
                        for filename in os.listdir(location_path):
                            if filename.endswith('.json'):
                                filepath = os.path.join(location_path, filename)
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        data = json.load(f)

                                        # Валидация данных
                                        if not isinstance(data, list):
                                            print(f"[ERROR] Invalid data format in {filepath}")
                                            continue

                                        # Имя файла: goal_type.json
                                        key = filename.replace('.json', '')
                                        workouts[level][location][key] = data
                                except json.JSONDecodeError as e:
                                    print(f"[ERROR] JSON decode error in {filepath}: {e}")
                                except IOError as e:
                                    print(f"[ERROR] File read error {filepath}: {e}")
                                except Exception as e:
                                    print(f"[ERROR] Unexpected error loading {filepath}: {e}")
                    except OSError as e:
                        print(f"[ERROR] Cannot list directory {location_path}: {e}")
        except Exception as e:
            print(f"[CRITICAL] Fatal error loading workouts: {e}")
            return {}

        return workouts

    def get_workout(self, goal: str, location: str, workout_type: str,
                    level: str = 'intermediate', exclude_recent: bool = True,
                    muscle_group: str = None) -> Dict[str, Any]:
        """
        Получить одно упражнение

        Args:
            goal: Цель (lose_weight, gain_weight, maintain_weight)
            location: Место (gym, home, both)
            workout_type: Тип (strength, cardio, flexibility, full_body)
            level: Уровень (beginner, intermediate, advanced)
            exclude_recent: Исключить недавно использованные
            muscle_group: Группа мышц (chest, back, legs, arms, shoulders, cardio, full_body)
        """
        try:
            # Валидация параметров
            if not all([goal, location, workout_type, level]):
                raise ValueError("Missing required parameters")

            # Формируем ключ для поиска
            file_key = f"{goal}_{workout_type}"

            exercises = self._get_exercises(level, location, file_key)

            if not exercises:
                print(f"[WARNING] No exercises found for {level}/{location}/{file_key}, using default")
                return self._create_default_workout(workout_type)

            # Фильтруем недавно использованные
            if exclude_recent:
                key = f"{level}_{location}_{file_key}"
                recent = self.used_exercises.get(key, [])
                available = [ex for ex in exercises if ex.get('Название упражнения') not in recent]

                if not available:
                    self.used_exercises[key] = []
                    available = exercises
            else:
                available = exercises

            selected = random.choice(available)

            # Добавляем в историю
            key = f"{level}_{location}_{file_key}"
            if key not in self.used_exercises:
                self.used_exercises[key] = []

            exercise_name = selected.get('Название упражнения', 'Unknown')
            self.used_exercises[key].append(exercise_name)

            # Ограничиваем историю
            if len(self.used_exercises[key]) > 20:
                self.used_exercises[key] = self.used_exercises[key][-20:]

            return selected
        except (ValueError, KeyError, IndexError) as e:
            print(f"[ERROR] Error getting workout: {e}")
            return self._create_default_workout(workout_type)
        except Exception as e:
            print(f"[CRITICAL] Unexpected error in get_workout: {e}")
            return self._create_default_workout(workout_type)

    def get_workouts(self, goal: str, location: str, workout_type: str,
                     level: str = 'intermediate', count: int = 10,
                     exclude_recent: bool = True, muscle_group: str = None) -> List[Dict[str, Any]]:
        """Получить несколько упражнений без повторений

        Args:
            muscle_group: Группа мышц для фильтрации (chest, back, legs, arms, shoulders)
        """

        file_key = f"{goal}_{workout_type}"
        exercises = self._get_exercises(level, location, file_key)

        # Фильтруем по группе мышц если указана
        if muscle_group and muscle_group not in ['full_body', 'cardio']:
            exercises = self._filter_by_muscle_group(exercises, muscle_group)

        if not exercises:
            return []

        # Фильтруем недавно использованные
        if exclude_recent:
            key = f"{level}_{location}_{file_key}"
            recent = self.used_exercises.get(key, [])
            available = [ex for ex in exercises if ex['Название упражнения'] not in recent]

            if len(available) < count:
                self.used_exercises[key] = []
                available = exercises
        else:
            available = exercises

        # Выбираем случайные упражнения
        selected = random.sample(available, min(count, len(available)))

        # Обновляем историю
        key = f"{level}_{location}_{file_key}"
        if key not in self.used_exercises:
            self.used_exercises[key] = []
        self.used_exercises[key].extend([ex['Название упражнения'] for ex in selected])

        if len(self.used_exercises[key]) > 20:
            self.used_exercises[key] = self.used_exercises[key][-20:]

        return selected

    def get_workout_plan_with_details(self, goal: str, location: str, workout_type: str,
                                       duration_minutes: int = 30,
                                       level: str = 'intermediate',
                                       muscle_group: str = None) -> Dict[str, Any]:
        """
        Создать детальный план тренировки с рекомендациями

        Args:
            muscle_group: Группа мышц для фильтрации упражнений
        """
        # Рассчитываем количество упражнений в зависимости от времени
        # 30 минут = 3-4 упражнения, 45 минут = 5-6, 60 минут = 6-8
        if duration_minutes <= 30:
            exercise_count = 3
        elif duration_minutes <= 45:
            exercise_count = 5
        elif duration_minutes <= 60:
            exercise_count = 6
        else:
            exercise_count = 8

        exercises = self.get_workouts(goal, location, workout_type, level,
                                      count=exercise_count,
                                      exclude_recent=True,
                                      muscle_group=muscle_group)

        # Получаем рекомендации
        recommendations = self.WORKOUT_RECOMMENDATIONS[goal][workout_type]

        # Расчет калорий
        calories_burned = self._calculate_calories(workout_type, duration_minutes)

        # Добавляем детали к каждому упражнению
        detailed_exercises = []
        for ex in exercises:
            detailed = ex.copy()

            # Если нет рекомендаций в упражнении, добавляем общие
            if 'Рекомендации' not in detailed:
                detailed['Рекомендации'] = {
                    'Подходы': recommendations['sets'],
                    'Повторения': recommendations['reps'],
                    'Отдых между подходами': recommendations['rest']
                }

            detailed_exercises.append(detailed)

        return {
            'goal': goal,
            'location': location,
            'duration_minutes': duration_minutes,
            'level': level,
            'type': workout_type,
            'exercises': detailed_exercises,
            'total_exercises': len(detailed_exercises),
            'recommendations': recommendations,
            'estimated_calories': calories_burned
        }

    def _get_exercises(self, level: str, location: str, file_key: str) -> List[Dict[str, Any]]:
        """Получить упражнения из файла"""

        if level not in self.workouts:
            level = 'intermediate'

        if location not in self.workouts[level]:
            # Пробуем 'both' как fallback
            if 'both' in self.workouts[level]:
                location = 'both'
            else:
                return []

        if file_key not in self.workouts[level][location]:
            return []

        return self.workouts[level][location][file_key]

    def _filter_by_muscle_group(self, exercises: List[Dict[str, Any]], muscle_group: str) -> List[Dict[str, Any]]:
        """
        Фильтрует упражнения по группе мышц с учетом СОВМЕЩЕНИЯ групп

        Args:
            exercises: Список упражнений
            muscle_group: chest, back, legs, arms, shoulders

        Returns:
            Отфильтрованный список упражнений с совмещенными группами
        """
        # Маппинг групп мышц на ключевые слова для поиска
        # Совмещаем группы как в реальном фитнесе!
        muscle_combinations = {
            'chest': {
                'primary': ['груд', 'chest', 'pectoral', 'pecs'],
                'secondary': ['трицепс', 'tricep', 'дельт', 'плеч', 'shoulder']  # Грудь + Трицепсы + Плечи
            },
            'back': {
                'primary': ['спин', 'широчайш', 'back', 'lat', 'трапеци', 'trapez'],
                'secondary': ['бицепс', 'bicep', 'предплеч', 'forearm']  # Спина + Бицепсы
            },
            'legs': {
                'primary': ['ног', 'ягодиц', 'квадрицепс', 'бедр', 'голен', 'икр', 'leg', 'quad', 'glute', 'calf', 'hamstring', 'thigh'],
                'secondary': ['пресс', 'abs', 'core', 'поясниц', 'lower back']  # Ноги + Пресс/Кор (для стабилизации)
            },
            'arms': {
                'primary': ['бицепс', 'трицепс', 'предплеч', 'bicep', 'tricep', 'forearm', 'arm'],
                'secondary': ['дельт', 'плеч', 'shoulder']  # Руки + Плечи
            },
            'shoulders': {
                'primary': ['дельт', 'плеч', 'shoulder', 'delt'],
                'secondary': ['трицепс', 'tricep', 'трапеци', 'trapez']  # Плечи + Трицепсы + Трапеции
            }
        }

        combination = muscle_combinations.get(muscle_group)
        if not combination:
            return exercises

        primary_keywords = combination['primary']
        secondary_keywords = combination['secondary']
        all_keywords = primary_keywords + secondary_keywords

        filtered = []
        for ex in exercises:
            muscle_text = ex.get('Мышечные группы', '') or ex.get('Работающие мышцы', '')
            muscle_text_lower = muscle_text.lower()

            # Проверяем есть ли хоть одно ключевое слово из primary или secondary
            if any(keyword in muscle_text_lower for keyword in all_keywords):
                filtered.append(ex)

        # Если после фильтрации ничего не осталось, возвращаем оригинальный список
        return filtered if filtered else exercises

    def _calculate_calories(self, workout_type: str, duration_minutes: int) -> int:
        """Расчет калорий"""
        return self.CALORIES_PER_MINUTE.get(workout_type, 6) * duration_minutes

    def _create_default_workout(self, workout_type: str) -> Dict[str, Any]:
        """Создать дефолтное упражнение если ничего не найдено"""
        return {
            'Название упражнения': 'Базовое упражнение',
            'Описание': 'Стандартное упражнение для данного типа тренировки',
            'Техника выполнения': 'Выполняйте упражнение согласно инструкции',
            'Важные моменты': ['Следите за техникой', 'Контролируйте дыхание'],
            'Работающие мышцы': 'Основные группы мышц',
            'Уровень': 'Продолжающий'
        }

    def get_stats(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Получить статистику по загруженным тренировкам"""
        stats: Dict[str, Dict[str, Dict[str, int]]] = {}

        for level in self.workouts:
            stats[level] = {}
            for location in self.workouts[level]:
                stats[level][location] = {}
                for key, exercises in self.workouts[level][location].items():
                    stats[level][location][key] = len(exercises)

        return stats

    def get_enhanced_workout_plan(self, goal: str, location: str, workout_type: str,
                                   duration_minutes: int = 30,
                                   level: str = 'intermediate',
                                   muscle_group: str = None,
                                   equipment_type: str = 'full',
                                   energy_level: str = 'medium',
                                   exercise_count: int = None) -> Dict[str, Any]:
        """
        УЛУЧШЕННЫЙ план тренировки с учетом всех параметров

        Args:
            equipment_type: 'bodyweight' (только вес тела), 'minimal' (минимум), 'full' (все)
            energy_level: 'high', 'medium', 'low', 'recovery'
            exercise_count: точное количество упражнений (если None - автоматически)
        """

        # 1. РАСЧЕТ количества упражнений если не указано
        if exercise_count is None:
            if duration_minutes <= 30:
                exercise_count = 3
            elif duration_minutes <= 45:
                exercise_count = 4
            elif duration_minutes <= 60:
                exercise_count = 5
            else:
                exercise_count = 6

            # Корректировка по энергии (НЕ уменьшаем ниже базового)
            if energy_level == 'high':
                exercise_count = min(7, exercise_count + 1)
            # При низкой энергии оставляем базовое количество

        # 2. ПОЛУЧАЕМ УПРАЖНЕНИЯ
        exercises = self.get_workouts(
            goal=goal,
            location=location,
            workout_type=workout_type,
            level=level,
            count=exercise_count * 2,  # Берем больше для фильтрации
            exclude_recent=True,
            muscle_group=muscle_group
        )

        # 3. ФИЛЬТРУЕМ ПО ОБОРУДОВАНИЮ И ДОБАВЛЯЕМ FALLBACK
        if equipment_type == 'bodyweight' and location == 'home':
            # КРИТИЧНО: только упражнения с весом тела!
            exercises = self._filter_bodyweight_only(exercises, muscle_group)

            # Если упражнений мало - добавляем fallback bodyweight
            if len(exercises) < exercise_count:
                bodyweight_fallback = self._get_bodyweight_exercises_for_group(muscle_group)
                for ex in bodyweight_fallback:
                    if len(exercises) >= exercise_count:
                        break
                    existing_names = [e.get('Название упражнения', '') for e in exercises]
                    if ex.get('Название упражнения', '') not in existing_names:
                        exercises.append(ex)

        # Если упражнений мало - добавляем fallback для зала
        if len(exercises) < exercise_count and location == 'gym':
            gym_fallback = self._get_gym_exercises_for_group(muscle_group)
            for ex in gym_fallback:
                if len(exercises) >= exercise_count:
                    break
                existing_names = [e.get('Название упражнения', '') for e in exercises]
                if ex.get('Название упражнения', '') not in existing_names:
                    exercises.append(ex)

        # Обрезаем до нужного количества
        exercises = exercises[:exercise_count]

        # 4. ДОБАВЛЯЕМ ДЕТАЛИ к каждому упражнению
        recommendations = self._get_smart_recommendations(goal, workout_type, level, energy_level)

        detailed_exercises = []
        for ex in exercises:
            detailed = ex.copy()

            # Добавляем рекомендации если их нет
            if 'Рекомендации' not in detailed:
                detailed['Рекомендации'] = self._generate_exercise_recommendations(
                    exercise=ex,
                    goal=goal,
                    level=level,
                    energy_level=energy_level
                )

            detailed_exercises.append(detailed)

        # 5. РАЗМИНКА (адаптивная)
        warmup = self._generate_warmup(duration_minutes, level, lang='ru')

        # 6. ЗАМИНКА (адаптивная)
        cooldown = self._generate_cooldown(duration_minutes, level, lang='ru')

        # 7. РАСЧЕТ КАЛОРИЙ (точный)
        calories_burned = self._calculate_precise_calories(
            workout_type=workout_type,
            duration_minutes=duration_minutes,
            level=level,
            energy_level=energy_level
        )

        return {
            'goal': goal,
            'location': location,
            'duration_minutes': duration_minutes,
            'level': level,
            'type': workout_type,
            'equipment_type': equipment_type,
            'energy_level': energy_level,
            'exercises': detailed_exercises,
            'total_exercises': len(detailed_exercises),
            'recommendations': recommendations,
            'estimated_calories': calories_burned,
            'warmup': warmup,
            'cooldown': cooldown
        }

    def _filter_bodyweight_only(self, exercises: List[Dict[str, Any]], muscle_group: str = None) -> List[Dict[str, Any]]:
        """Фильтр: упражнения с весом тела для конкретной группы мышц"""

        # Слова-исключения (требуют оборудования)
        equipment_keywords = [
            'штанга', 'гантел', 'тренажер', 'блок', 'скамья',
            'barbell', 'dumbbell', 'machine', 'bench', 'cable'
        ]

        filtered = []
        for ex in exercises:
            name = ex.get('Название упражнения', '').lower()
            description = ex.get('Описание', '').lower()
            technique = str(ex.get('Техника выполнения', '')).lower()

            full_text = f"{name} {description} {technique}"

            # Проверяем что НЕТ оборудования
            has_equipment = any(keyword in full_text for keyword in equipment_keywords)

            if not has_equipment:
                filtered.append(ex)

        # Если мало упражнений - добавляем базовые для конкретной группы мышц
        if len(filtered) < 5:
            filtered = self._get_bodyweight_exercises_for_group(muscle_group)

        return filtered

    def _get_bodyweight_exercises_for_group(self, muscle_group: str = None) -> List[Dict[str, Any]]:
        """Получить bodyweight упражнения для конкретной группы мышц"""

        # СПИНА + БИЦЕПС
        back_biceps = [
            {
                'Название упражнения': 'Супермен',
                'Техника выполнения': 'Лягте на живот, руки вытянуты вперед. Одновременно поднимите руки и ноги от пола, задержитесь на 2-3 секунды.',
                'Работающие мышцы': 'Спина, ягодицы, задняя поверхность бедра'
            },
            {
                'Название упражнения': 'Обратные отжимания от пола',
                'Техника выполнения': 'Лягте на живот, руки вдоль тела. Поднимите грудь и руки от пола, сводя лопатки.',
                'Работающие мышцы': 'Спина, задние дельты, бицепс'
            },
            {
                'Название упражнения': 'Лодочка',
                'Техника выполнения': 'Лягте на живот. Поднимите одновременно руки и ноги, удерживайте положение.',
                'Работающие мышцы': 'Разгибатели спины, ягодицы'
            },
            {
                'Название упражнения': 'Планка с подъемом руки',
                'Техника выполнения': 'В позиции планки поочередно поднимайте руки вперед, удерживая баланс.',
                'Работающие мышцы': 'Спина, кор, плечи'
            },
            {
                'Название упражнения': 'Скалолаз',
                'Техника выполнения': 'В упоре лежа поочередно подтягивайте колени к груди в быстром темпе.',
                'Работающие мышцы': 'Кор, спина, плечи'
            }
        ]

        # ГРУДЬ + ТРИЦЕПС
        chest_triceps = [
            {
                'Название упражнения': 'Отжимания от пола',
                'Техника выполнения': 'Упор лежа, руки на ширине плеч. Опуститесь до касания грудью пола, выжмите себя вверх.',
                'Работающие мышцы': 'Грудь, трицепсы, передние дельты'
            },
            {
                'Название упражнения': 'Отжимания узким хватом',
                'Техника выполнения': 'Отжимания с узкой постановкой рук (ладони рядом). Локти прижаты к корпусу.',
                'Работающие мышцы': 'Трицепсы, грудь'
            },
            {
                'Название упражнения': 'Отжимания с широкой постановкой рук',
                'Техника выполнения': 'Руки шире плеч. Больше нагрузка на грудные мышцы.',
                'Работающие мышцы': 'Грудь, передние дельты'
            },
            {
                'Название упражнения': 'Обратные отжимания от стула',
                'Техника выполнения': 'Руки на стуле сзади, ноги вытянуты. Опускайтесь сгибая локти до 90 градусов.',
                'Работающие мышцы': 'Трицепсы, грудь, плечи'
            },
            {
                'Название упражнения': 'Алмазные отжимания',
                'Техника выполнения': 'Ладони образуют ромб под грудью. Отжимайтесь, локти вдоль корпуса.',
                'Работающие мышцы': 'Трицепсы, грудь'
            }
        ]

        # НОГИ + ПЛЕЧИ
        legs_shoulders = [
            {
                'Название упражнения': 'Приседания',
                'Техника выполнения': 'Ноги на ширине плеч, спина прямая. Опуститесь до параллели бедер с полом.',
                'Работающие мышцы': 'Квадрицепсы, ягодицы'
            },
            {
                'Название упражнения': 'Выпады',
                'Техника выполнения': 'Шаг вперед, опуститесь до касания коленом пола. Вернитесь в исходное.',
                'Работающие мышцы': 'Квадрицепсы, ягодицы, икры'
            },
            {
                'Название упражнения': 'Приседания с выпрыгиванием',
                'Техника выполнения': 'Присед и мощный прыжок вверх. Мягкое приземление.',
                'Работающие мышцы': 'Квадрицепсы, ягодицы, икры'
            },
            {
                'Название упражнения': 'Отжимания уголком',
                'Техника выполнения': 'Ноги на возвышении, таз поднят. Отжимайтесь головой вниз.',
                'Работающие мышцы': 'Плечи, трицепсы'
            },
            {
                'Название упражнения': 'Ягодичный мостик',
                'Техника выполнения': 'Лежа на спине, ноги согнуты. Поднимайте таз вверх, сжимая ягодицы.',
                'Работающие мышцы': 'Ягодицы, задняя поверхность бедра'
            }
        ]

        # РУКИ + ПЛЕЧИ
        arms_shoulders = [
            {
                'Название упражнения': 'Отжимания узким хватом',
                'Техника выполнения': 'Узкая постановка рук, локти прижаты к корпусу.',
                'Работающие мышцы': 'Трицепсы, грудь'
            },
            {
                'Название упражнения': 'Обратные отжимания',
                'Техника выполнения': 'Руки на опоре сзади, сгибайте локти до 90 градусов.',
                'Работающие мышцы': 'Трицепсы, плечи'
            },
            {
                'Название упражнения': 'Отжимания уголком',
                'Техника выполнения': 'Таз поднят вверх, отжимайтесь головой вниз.',
                'Работающие мышцы': 'Плечи, трицепсы'
            },
            {
                'Название упражнения': 'Планка с касанием плеча',
                'Техника выполнения': 'В планке поочередно касайтесь рукой противоположного плеча.',
                'Работающие мышцы': 'Плечи, кор, руки'
            },
            {
                'Название упражнения': 'Круговые движения руками',
                'Техника выполнения': 'Руки в стороны, выполняйте круговые движения с напряжением.',
                'Работающие мышцы': 'Плечи, руки'
            }
        ]

        # ПОЛНОЕ ТЕЛО
        full_body = [
            {
                'Название упражнения': 'Берпи',
                'Техника выполнения': 'Присед, прыжок в планку, отжимание, прыжок вверх.',
                'Работающие мышцы': 'Все тело'
            },
            {
                'Название упражнения': 'Скалолаз',
                'Техника выполнения': 'В упоре лежа быстро подтягивайте колени к груди поочередно.',
                'Работающие мышцы': 'Кор, ноги, плечи'
            },
            {
                'Название упражнения': 'Приседания с выпрыгиванием',
                'Техника выполнения': 'Присед и мощный прыжок вверх.',
                'Работающие мышцы': 'Ноги, ягодицы'
            },
            {
                'Название упражнения': 'Отжимания',
                'Техника выполнения': 'Классические отжимания от пола.',
                'Работающие мышцы': 'Грудь, трицепсы, плечи'
            },
            {
                'Название упражнения': 'Планка',
                'Техника выполнения': 'Удержание тела в прямой линии на предплечьях.',
                'Работающие мышцы': 'Кор, плечи, спина'
            }
        ]

        # Выбираем упражнения по группе мышц
        if muscle_group == 'back':
            return back_biceps
        elif muscle_group == 'chest':
            return chest_triceps
        elif muscle_group == 'legs':
            return legs_shoulders
        elif muscle_group == 'arms' or muscle_group == 'shoulders':
            return arms_shoulders
        else:
            return full_body

    def _get_gym_exercises_for_group(self, muscle_group: str = None) -> List[Dict[str, Any]]:
        """Получить упражнения для зала для конкретной группы мышц"""

        # СПИНА + БИЦЕПС (зал)
        back_biceps_gym = [
            {
                'Название упражнения': 'Тяга верхнего блока к груди',
                'Техника выполнения': 'Сядьте в тренажер, возьмите рукоять широким хватом. Тяните к верхней части груди, сводя лопатки. Медленно вернитесь в исходное положение.',
                'Важные моменты': ['Не отклоняйтесь назад', 'Тяните локтями, не руками', 'Сводите лопатки в нижней точке'],
                'Работающие мышцы': 'Широчайшие, бицепс, ромбовидные'
            },
            {
                'Название упражнения': 'Тяга штанги в наклоне',
                'Техника выполнения': 'Наклонитесь вперед, спина прямая, колени слегка согнуты. Тяните штангу к животу, сводя лопатки.',
                'Важные моменты': ['Спина прямая', 'Локти вдоль корпуса', 'Не используйте инерцию'],
                'Работающие мышцы': 'Широчайшие, ромбовидные, бицепс'
            },
            {
                'Название упражнения': 'Тяга гантели одной рукой',
                'Техника выполнения': 'Упритесь коленом и рукой в скамью. Тяните гантель к поясу, локоть идет вверх и назад.',
                'Важные моменты': ['Спина параллельна полу', 'Не вращайте корпус', 'Полная амплитуда'],
                'Работающие мышцы': 'Широчайшие, ромбовидные, бицепс'
            },
            {
                'Название упражнения': 'Подтягивания',
                'Техника выполнения': 'Хват шире плеч, ладони от себя. Подтянитесь до подбородка выше перекладины. Опуститесь контролируемо.',
                'Важные моменты': ['Не раскачивайтесь', 'Сводите лопатки', 'Полное разгибание рук внизу'],
                'Работающие мышцы': 'Широчайшие, бицепс, предплечья'
            },
            {
                'Название упражнения': 'Сгибание рук со штангой',
                'Техника выполнения': 'Стойте прямо, штанга в опущенных руках. Сгибайте руки, поднимая штангу к плечам. Локти неподвижны.',
                'Важные моменты': ['Локти прижаты к корпусу', 'Не раскачивайтесь', 'Контролируйте негативную фазу'],
                'Работающие мышцы': 'Бицепс, предплечья'
            }
        ]

        # ГРУДЬ + ТРИЦЕПС (зал)
        chest_triceps_gym = [
            {
                'Название упражнения': 'Жим штанги лежа',
                'Техника выполнения': 'Лягте на скамью, хват чуть шире плеч. Опустите штангу к середине груди, выжмите вверх.',
                'Важные моменты': ['Лопатки сведены', 'Ноги упираются в пол', 'Не отрывайте таз'],
                'Работающие мышцы': 'Грудь, трицепс, передние дельты'
            },
            {
                'Название упражнения': 'Жим гантелей на наклонной скамье',
                'Техника выполнения': 'Скамья под углом 30-45°. Выжимайте гантели вверх, сводя их в верхней точке.',
                'Важные моменты': ['Локти под углом 45°', 'Полная амплитуда', 'Контроль веса'],
                'Работающие мышцы': 'Верхняя часть груди, передние дельты'
            },
            {
                'Название упражнения': 'Сведение рук в кроссовере',
                'Техника выполнения': 'Стойте между блоками, руки разведены. Сводите руки перед собой, напрягая грудь.',
                'Важные моменты': ['Легкий наклон вперед', 'Локти слегка согнуты', 'Пиковое сокращение'],
                'Работающие мышцы': 'Грудь'
            },
            {
                'Название упражнения': 'Французский жим лежа',
                'Техника выполнения': 'Лежа на скамье, штанга над головой. Сгибайте локти, опуская штангу ко лбу. Разгибайте руки.',
                'Важные моменты': ['Локти неподвижны', 'Контроль веса', 'Полное разгибание'],
                'Работающие мышцы': 'Трицепс'
            },
            {
                'Название упражнения': 'Разгибание рук на блоке',
                'Техника выполнения': 'Стойте перед верхним блоком. Разгибайте руки вниз, прижимая локти к корпусу.',
                'Важные моменты': ['Локти неподвижны', 'Полное разгибание', 'Пиковое сокращение'],
                'Работающие мышцы': 'Трицепс'
            }
        ]

        # НОГИ (зал)
        legs_gym = [
            {
                'Название упражнения': 'Приседания со штангой',
                'Техника выполнения': 'Штанга на трапециях, ноги на ширине плеч. Приседайте до параллели, вставайте мощно.',
                'Важные моменты': ['Спина прямая', 'Колени по направлению носков', 'Не заваливайтесь вперед'],
                'Работающие мышцы': 'Квадрицепсы, ягодицы, бицепс бедра'
            },
            {
                'Название упражнения': 'Жим ногами',
                'Техника выполнения': 'Сядьте в тренажер, ноги на платформе. Опускайте платформу, сгибая колени до 90°. Выжимайте вверх.',
                'Важные моменты': ['Поясница прижата', 'Не разгибайте колени полностью', 'Контроль веса'],
                'Работающие мышцы': 'Квадрицепсы, ягодицы'
            },
            {
                'Название упражнения': 'Выпады с гантелями',
                'Техника выполнения': 'Гантели в руках, шаг вперед. Опуститесь до касания коленом пола. Вернитесь в исходное.',
                'Важные моменты': ['Колено не выходит за носок', 'Спина прямая', 'Контроль баланса'],
                'Работающие мышцы': 'Квадрицепсы, ягодицы, бицепс бедра'
            },
            {
                'Название упражнения': 'Сгибание ног в тренажере',
                'Техника выполнения': 'Лежа на животе, валик на щиколотках. Сгибайте ноги, подтягивая пятки к ягодицам.',
                'Важные моменты': ['Бедра прижаты', 'Полная амплитуда', 'Пиковое сокращение'],
                'Работающие мышцы': 'Бицепс бедра'
            },
            {
                'Название упражнения': 'Разгибание ног в тренажере',
                'Техника выполнения': 'Сидя в тренажере, валик на голенях. Разгибайте ноги полностью, напрягая квадрицепсы.',
                'Важные моменты': ['Спина прижата', 'Полное разгибание', 'Контролируйте негативную фазу'],
                'Работающие мышцы': 'Квадрицепсы'
            }
        ]

        # ПЛЕЧИ (зал)
        shoulders_gym = [
            {
                'Название упражнения': 'Жим гантелей сидя',
                'Техника выполнения': 'Сидя на скамье со спинкой, гантели у плеч. Выжимайте вверх, сводя гантели в верхней точке.',
                'Важные моменты': ['Спина прижата', 'Локти под гантелями', 'Не разгибайте локти полностью'],
                'Работающие мышцы': 'Передние и средние дельты, трицепс'
            },
            {
                'Название упражнения': 'Разведение гантелей в стороны',
                'Техника выполнения': 'Стойте прямо, гантели по бокам. Поднимайте руки в стороны до уровня плеч.',
                'Важные моменты': ['Локти слегка согнуты', 'Не поднимайте плечи', 'Контроль негативной фазы'],
                'Работающие мышцы': 'Средние дельты'
            },
            {
                'Название упражнения': 'Тяга штанги к подбородку',
                'Техника выполнения': 'Узкий хват, тяните штангу вдоль тела к подбородку. Локти выше кистей.',
                'Важные моменты': ['Локти ведут движение', 'Не поднимайте слишком высоко', 'Контроль веса'],
                'Работающие мышцы': 'Средние дельты, трапеции'
            },
            {
                'Название упражнения': 'Разведение в наклоне',
                'Техника выполнения': 'Наклон вперед, гантели внизу. Разводите руки в стороны, сводя лопатки.',
                'Важные моменты': ['Спина прямая', 'Локти слегка согнуты', 'Пиковое сокращение'],
                'Работающие мышцы': 'Задние дельты'
            },
            {
                'Название упражнения': 'Жим Арнольда',
                'Техника выполнения': 'Гантели перед собой, ладони к себе. Разворачивайте и выжимайте вверх одновременно.',
                'Важные моменты': ['Плавное движение', 'Полная амплитуда', 'Контроль веса'],
                'Работающие мышцы': 'Все пучки дельт'
            }
        ]

        # РУКИ (зал)
        arms_gym = [
            {
                'Название упражнения': 'Сгибание рук со штангой',
                'Техника выполнения': 'Стойте прямо, хват на ширине плеч. Сгибайте руки, локти неподвижны.',
                'Важные моменты': ['Не раскачивайтесь', 'Локти прижаты', 'Полная амплитуда'],
                'Работающие мышцы': 'Бицепс'
            },
            {
                'Название упражнения': 'Сгибание рук с гантелями "молот"',
                'Техника выполнения': 'Гантели нейтральным хватом. Сгибайте руки поочередно или вместе.',
                'Важные моменты': ['Локти неподвижны', 'Нейтральный хват', 'Контроль движения'],
                'Работающие мышцы': 'Бицепс, брахиалис, предплечья'
            },
            {
                'Название упражнения': 'Французский жим с гантелей',
                'Техника выполнения': 'Сидя или стоя, гантель за головой. Разгибайте руки вверх, локти неподвижны.',
                'Важные моменты': ['Локти направлены вверх', 'Полное разгибание', 'Контроль веса'],
                'Работающие мышцы': 'Трицепс'
            },
            {
                'Название упражнения': 'Разгибание рук на блоке',
                'Техника выполнения': 'Верхний блок, разгибайте руки вниз до полного выпрямления.',
                'Важные моменты': ['Локти прижаты', 'Полное разгибание', 'Пиковое сокращение'],
                'Работающие мышцы': 'Трицепс'
            },
            {
                'Название упражнения': 'Концентрированные сгибания',
                'Техника выполнения': 'Сидя, локоть упирается во внутреннюю часть бедра. Сгибайте руку с гантелей.',
                'Важные моменты': ['Локоть неподвижен', 'Пиковое сокращение', 'Контроль негативной фазы'],
                'Работающие мышцы': 'Бицепс'
            }
        ]

        # ПОЛНОЕ ТЕЛО (зал)
        full_body_gym = [
            {
                'Название упражнения': 'Становая тяга',
                'Техника выполнения': 'Штанга на полу, хват на ширине плеч. Поднимайте, разгибая ноги и спину одновременно.',
                'Важные моменты': ['Спина прямая', 'Штанга близко к телу', 'Не округляйте поясницу'],
                'Работающие мышцы': 'Спина, ноги, ягодицы, предплечья'
            },
            {
                'Название упражнения': 'Приседания со штангой',
                'Техника выполнения': 'Штанга на трапециях. Приседайте до параллели, вставайте мощно.',
                'Важные моменты': ['Спина прямая', 'Колени по носкам', 'Грудь вперед'],
                'Работающие мышцы': 'Квадрицепсы, ягодицы'
            },
            {
                'Название упражнения': 'Жим штанги лежа',
                'Техника выполнения': 'Лежа на скамье, опустите штангу к груди и выжмите вверх.',
                'Важные моменты': ['Лопатки сведены', 'Ноги упираются', 'Контроль веса'],
                'Работающие мышцы': 'Грудь, трицепс, плечи'
            },
            {
                'Название упражнения': 'Тяга верхнего блока',
                'Техника выполнения': 'Широкий хват, тяните к груди, сводя лопатки.',
                'Важные моменты': ['Не отклоняйтесь', 'Тяните локтями', 'Полная амплитуда'],
                'Работающие мышцы': 'Спина, бицепс'
            },
            {
                'Название упражнения': 'Жим гантелей сидя',
                'Техника выполнения': 'Сидя, выжимайте гантели вверх от плеч.',
                'Важные моменты': ['Спина прижата', 'Контроль веса', 'Не разгибайте локти полностью'],
                'Работающие мышцы': 'Плечи, трицепс'
            }
        ]

        # Выбираем упражнения по группе мышц
        if muscle_group == 'back':
            return back_biceps_gym
        elif muscle_group == 'chest':
            return chest_triceps_gym
        elif muscle_group == 'legs':
            return legs_gym
        elif muscle_group == 'shoulders':
            return shoulders_gym
        elif muscle_group == 'arms':
            return arms_gym
        else:
            return full_body_gym

    def _get_smart_recommendations(self, goal: str, workout_type: str,
                                    level: str, energy_level: str) -> Dict[str, str]:
        """Умные рекомендации с учетом ВСЕХ параметров"""

        base = self.WORKOUT_RECOMMENDATIONS.get(goal, {}).get(workout_type, {})

        # Корректируем по уровню энергии
        if energy_level == 'low' or energy_level == 'recovery':
            # Меньше подходов, больше отдыха
            return {
                'sets': '2-3',
                'reps': base.get('reps', '10-12'),
                'rest': '90-120 сек'
            }
        elif energy_level == 'high':
            # Больше интенсивности
            return {
                'sets': '4-5',
                'reps': base.get('reps', '12-15'),
                'rest': '30-45 сек'
            }

        return base

    def _generate_exercise_recommendations(self, exercise: Dict, goal: str,
                                            level: str, energy_level: str) -> Dict[str, str]:
        """Генерация УНИКАЛЬНЫХ рекомендаций для каждого упражнения"""

        # Базовые значения по уровню
        if level == 'beginner':
            sets_range = '2-3'
            reps_base = 10
            rest = '90 сек'
        elif level == 'intermediate':
            sets_range = '3-4'
            reps_base = 12
            rest = '60 сек'
        else:  # advanced
            sets_range = '4-5'
            reps_base = 15
            rest = '45 сек'

        # Корректировка по цели
        if goal == 'lose_weight':
            reps_base += 3  # Больше повторений
            rest = '30-45 сек'  # Меньше отдыха
        elif goal == 'gain_weight':
            reps_base -= 4  # Меньше повторений, больше вес
            rest = '90-120 сек'  # Больше отдыха

        # Корректировка по энергии
        if energy_level in ['low', 'recovery']:
            sets_range = '2-3'
            rest = '120 сек'
        elif energy_level == 'high':
            reps_base += 2

        return {
            'Подходы': sets_range,
            'Повторения': f'{max(6, reps_base-2)}-{reps_base+2}',
            'Отдых между подходами': rest
        }

    def _generate_warmup(self, duration: int, level: str, lang: str = 'ru') -> List[Dict[str, str]]:
        """Генерация адаптивной разминки"""

        warmup_exercises = {
            'ru': [
                {'name': '🏃 Легкий бег на месте', 'duration': '2-3 мин'},
                {'name': '🔄 Вращения руками', 'duration': '1 мин'},
                {'name': '🦵 Махи ногами', 'duration': '1 мин'},
                {'name': '🌀 Вращения корпусом', 'duration': '1 мин'},
                {'name': '🧘 Наклоны в стороны', 'duration': '1 мин'}
            ],
            'en': [
                {'name': '🏃 Light jogging in place', 'duration': '2-3 min'},
                {'name': '🔄 Arm circles', 'duration': '1 min'},
                {'name': '🦵 Leg swings', 'duration': '1 min'},
                {'name': '🌀 Torso rotations', 'duration': '1 min'},
                {'name': '🧘 Side bends', 'duration': '1 min'}
            ]
        }

        exercises = warmup_exercises.get(lang, warmup_exercises['ru'])

        # Адаптируем под время
        if duration <= 30:
            return exercises[:3]  # Короткая разминка
        elif duration <= 45:
            return exercises[:4]
        else:
            return exercises  # Полная разминка

    def _generate_cooldown(self, duration: int, level: str, lang: str = 'ru') -> List[Dict[str, str]]:
        """Генерация адаптивной заминки"""

        cooldown_exercises = {
            'ru': [
                {'name': '🧘 Растяжка квадрицепсов', 'duration': '30-60 сек каждая нога'},
                {'name': '🦵 Растяжка задней поверхности', 'duration': '30-60 сек'},
                {'name': '💪 Растяжка грудных мышц', 'duration': '30-60 сек'},
                {'name': '🤸 Растяжка плеч', 'duration': '30-60 сек'},
                {'name': '🧘 Глубокое дыхание', 'duration': '2-3 мин'}
            ],
            'en': [
                {'name': '🧘 Quadriceps stretch', 'duration': '30-60 sec each leg'},
                {'name': '🦵 Hamstring stretch', 'duration': '30-60 sec'},
                {'name': '💪 Chest stretch', 'duration': '30-60 sec'},
                {'name': '🤸 Shoulder stretch', 'duration': '30-60 sec'},
                {'name': '🧘 Deep breathing', 'duration': '2-3 min'}
            ]
        }

        exercises = cooldown_exercises.get(lang, cooldown_exercises['ru'])

        if duration <= 30:
            return exercises[:3]
        else:
            return exercises

    def _calculate_precise_calories(self, workout_type: str, duration_minutes: int,
                                     level: str, energy_level: str) -> int:
        """Точный расчет калорий с учетом ВСЕХ факторов"""

        base_cal_per_min = self.CALORIES_PER_MINUTE.get(workout_type, 6)

        # Корректировка по уровню
        level_multiplier = {
            'beginner': 0.8,
            'intermediate': 1.0,
            'advanced': 1.2
        }.get(level, 1.0)

        # Корректировка по энергии
        energy_multiplier = {
            'recovery': 0.6,
            'low': 0.8,
            'medium': 1.0,
            'high': 1.3
        }.get(energy_level, 1.0)

        total_calories = int(base_cal_per_min * duration_minutes * level_multiplier * energy_multiplier)

        return total_calories

    def save_workout_feedback(self, user_id: int, difficulty: str,
                              exercises_completed: List[str] = None,
                              notes: str = None):
        """
        Сохранить детальную обратную связь о тренировке

        Args:
            difficulty: 'easy', 'perfect', 'hard'
            exercises_completed: список завершенных упражнений
            notes: заметки пользователя
        """
        try:
            with open(self.workout_history_file, 'r', encoding='utf-8') as f:
                all_history = json.load(f)

            user_key = str(user_id)
            if user_key not in all_history:
                all_history[user_key] = {'workouts': [], 'exercises': {}}

            user_history = all_history[user_key]

            # Обновляем последнюю тренировку
            if user_history['workouts']:
                last_workout = user_history['workouts'][-1]
                last_workout['difficulty'] = difficulty
                last_workout['completed'] = True
                last_workout['completion_date'] = datetime.now().isoformat()

                if exercises_completed:
                    last_workout['exercises_completed'] = exercises_completed

                if notes:
                    last_workout['notes'] = notes

                # Корректируем будущие планы на основе фидбека
                if difficulty == 'hard':
                    last_workout['adjustment'] = 'decrease_intensity'
                elif difficulty == 'easy':
                    last_workout['adjustment'] = 'increase_intensity'
                else:
                    last_workout['adjustment'] = 'maintain'

            # Сохраняем
            with open(self.workout_history_file, 'w', encoding='utf-8') as f:
                json.dump(all_history, f, ensure_ascii=False, indent=2)

            print(f"[OK] Feedback saved for user {user_id}")

        except Exception as e:
            print(f"[ERROR] Error saving feedback: {e}")

    def save_workout_to_history(self, user_id: int, workout_data: Dict):
        """Сохранить тренировку в историю"""
        try:
            with open(self.workout_history_file, 'r', encoding='utf-8') as f:
                all_history = json.load(f)

            user_key = str(user_id)
            if user_key not in all_history:
                all_history[user_key] = {'workouts': [], 'exercises': {}}

            # Добавляем тренировку
            workout_entry = {
                'date': datetime.now().isoformat(),
                'duration': workout_data.get('duration_minutes', 45),
                'calories': workout_data.get('estimated_calories', 0),
                'exercises_count': len(workout_data.get('exercises', [])),
                'type': workout_data.get('type', 'strength'),
                'location': workout_data.get('location', 'gym'),
                'level': workout_data.get('level', 'intermediate'),
                'completed': False
            }

            all_history[user_key]['workouts'].append(workout_entry)

            # Ограничиваем историю последними 100 тренировками
            if len(all_history[user_key]['workouts']) > 100:
                all_history[user_key]['workouts'] = all_history[user_key]['workouts'][-100:]

            with open(self.workout_history_file, 'w', encoding='utf-8') as f:
                json.dump(all_history, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[ERROR] Error saving workout to history: {e}")

    def analyze_user_progress(self, user_id: int) -> Dict:
        """
        ПОЛНЫЙ АНАЛИЗ прогресса пользователя

        Returns:
            {
                'total_workouts': int,
                'streak_days': int,
                'best_streak': int,
                'strength_progress': {exercise: percent},
                'weak_points': [str],
                'recommendations': [str],
                'training_volume': int,
                'recovery_status': str
            }
        """
        history = self._load_workout_history(user_id)

        if not history or not history.get('workouts'):
            return None

        workouts = history['workouts']
        exercises = history.get('exercises', {})

        # 1. Базовая статистика
        total_workouts = len(workouts)

        # 2. Серии тренировок (streak)
        streak_days, best_streak = self._calculate_streaks(workouts)

        # 3. Прогресс по силе
        strength_progress = {}
        for exercise_name, exercise_history in exercises.items():
            if len(exercise_history) >= 2:
                first_weight = exercise_history[0].get('weight', 0)
                last_weight = exercise_history[-1].get('weight', 0)

                if first_weight > 0:
                    progress_percent = ((last_weight - first_weight) / first_weight) * 100
                    strength_progress[exercise_name] = round(progress_percent, 1)

        # 4. Анализ слабых мест
        weak_points = self._identify_weak_points(exercises, workouts)

        # 5. Персональные рекомендации
        recommendations = self._generate_personal_recommendations(
            workouts, exercises, strength_progress
        )

        # 6. Объем тренировок
        training_volume = sum(w.get('exercises_count', 0) for w in workouts[-4:])

        # 7. Статус восстановления
        recovery_status = self._assess_recovery(workouts)

        return {
            'total_workouts': total_workouts,
            'streak_days': streak_days,
            'best_streak': best_streak,
            'strength_progress': strength_progress,
            'weak_points': weak_points,
            'recommendations': recommendations,
            'training_volume': training_volume,
            'recovery_status': recovery_status
        }

    def _calculate_streaks(self, workouts: List[Dict]) -> tuple:
        """Рассчитать серии тренировок"""
        if not workouts:
            return 0, 0

        # Группируем по дням
        workout_dates = []
        for w in workouts:
            try:
                date = datetime.fromisoformat(w['date']).date()
                if date not in workout_dates:
                    workout_dates.append(date)
            except:
                continue

        if not workout_dates:
            return 0, 0

        workout_dates.sort()

        # Текущая серия
        current_streak = 0
        today = datetime.now().date()

        for i in range(len(workout_dates) - 1, -1, -1):
            date = workout_dates[i]
            days_ago = (today - date).days

            if days_ago <= current_streak + 1:
                current_streak = days_ago
            else:
                break

        # Лучшая серия
        best_streak = 1
        current = 1

        for i in range(1, len(workout_dates)):
            diff = (workout_dates[i] - workout_dates[i-1]).days
            if diff == 1:
                current += 1
                best_streak = max(best_streak, current)
            else:
                current = 1

        return current_streak, best_streak

    def _identify_weak_points(self, exercises: Dict, workouts: List[Dict]) -> List[str]:
        """Определить слабые места"""
        weak_points = []

        # Анализ прогресса по упражнениям
        stagnant_exercises = []
        for exercise_name, exercise_history in exercises.items():
            if len(exercise_history) >= 5:
                # Проверяем последние 5 тренировок
                recent_weights = [w.get('weight', 0) for w in exercise_history[-5:]]

                # Если вес не менялся
                if len(set(recent_weights)) == 1 and recent_weights[0] > 0:
                    stagnant_exercises.append(exercise_name)

        if stagnant_exercises:
            weak_points.append(f"Застой в упражнениях: {', '.join(stagnant_exercises[:2])}")

        # Анализ частоты тренировок
        if len(workouts) >= 4:
            try:
                recent_workouts = workouts[-4:]
                dates = [datetime.fromisoformat(w['date']).date() for w in recent_workouts]

                if dates:
                    days_range = (max(dates) - min(dates)).days
                    if days_range > 14:
                        weak_points.append("Нерегулярные тренировки - старайтесь 3-4 раза в неделю")
            except:
                pass

        # Анализ сложности
        recent_difficulties = [w.get('difficulty') for w in workouts[-3:] if w.get('difficulty')]
        if recent_difficulties.count('hard') >= 2:
            weak_points.append("Слишком высокая интенсивность - риск перетренированности")
        elif recent_difficulties.count('easy') >= 2:
            weak_points.append("Низкая интенсивность - пора увеличивать нагрузку")

        return weak_points

    def _generate_personal_recommendations(self, workouts: List[Dict],
                                           exercises: Dict,
                                           strength_progress: Dict) -> List[str]:
        """Генерация УМНЫХ персональных рекомендаций"""
        recommendations = []

        # 1. Рекомендации по прогрессу
        if strength_progress:
            avg_progress = sum(strength_progress.values()) / len(strength_progress)

            if avg_progress < 5:
                recommendations.append(
                    "Прогресс замедлился. Попробуйте методику 'двойная прогрессия': "
                    "сначала увеличивайте повторения (до 15), затем вес"
                )
            elif avg_progress > 20:
                recommendations.append(
                    "Отличный прогресс! Продолжайте в том же духе, но следите за техникой"
                )

        # 2. Рекомендации по объему
        if len(workouts) >= 4:
            total_volume = sum(w.get('exercises_count', 0) for w in workouts[-4:])

            if total_volume < 20:
                recommendations.append(
                    "Увеличьте объем тренировок: добавьте 1-2 упражнения в каждую сессию"
                )
            elif total_volume > 50:
                recommendations.append(
                    "Высокий объем тренировок - убедитесь что восстанавливаетесь полностью"
                )

        # 3. Рекомендации по частоте
        if len(workouts) >= 7:
            try:
                last_week = [w for w in workouts if
                             (datetime.now() - datetime.fromisoformat(w['date'])).days <= 7]

                if len(last_week) < 3:
                    recommendations.append(
                        "Тренируйтесь чаще! Оптимально 3-5 раз в неделю для лучших результатов"
                    )
                elif len(last_week) > 6:
                    recommendations.append(
                        "Отдых тоже важен! Добавьте 1-2 дня полного отдыха в неделю"
                    )
            except:
                pass

        # 4. Мотивационные рекомендации
        if len(workouts) >= 10:
            recommendations.append(
                f"💪 Вы уже выполнили {len(workouts)} тренировок! "
                "Каждая тренировка делает вас сильнее!"
            )

        return recommendations[:5]  # Максимум 5 рекомендаций

    def _assess_recovery(self, workouts: List[Dict]) -> str:
        """Оценить статус восстановления"""
        if len(workouts) < 2:
            return "normal"

        # Проверяем последние тренировки
        recent = workouts[-3:] if len(workouts) >= 3 else workouts

        # Если все последние тренировки были "сложными"
        hard_count = sum(1 for w in recent if w.get('difficulty') == 'hard')

        if hard_count >= 2:
            return "overtraining_risk"

        # Проверяем частоту
        if len(workouts) >= 7:
            try:
                last_week = [w for w in workouts if
                             (datetime.now() - datetime.fromisoformat(w['date'])).days <= 7]

                if len(last_week) > 6:
                    return "high_frequency"
            except:
                pass

        return "normal"

    def get_detailed_analysis(self, user_id: int) -> Dict:
        """
        ДЕТАЛЬНАЯ статистика для отображения пользователю
        """
        history = self._load_workout_history(user_id)

        if not history or not history.get('workouts'):
            return {'total_workouts': 0}

        workouts = history['workouts']
        exercises = history.get('exercises', {})

        # Базовая статистика
        total_workouts = len(workouts)
        total_time = sum(w.get('duration', 0) for w in workouts)
        total_calories = sum(w.get('calories', 0) for w in workouts)

        # Серии
        current_streak, best_streak = self._calculate_streaks(workouts)

        # Прогресс по весам
        weight_progress = {}
        for exercise_name, exercise_history in exercises.items():
            if len(exercise_history) >= 2:
                first = exercise_history[0].get('weight', 0)
                last = exercise_history[-1].get('weight', 0)
                weight_progress[exercise_name] = {
                    'first': first,
                    'last': last,
                    'increase': last - first
                }

        # Любимые упражнения
        exercise_counts = {}
        for exercise_name, exercise_history in exercises.items():
            exercise_counts[exercise_name] = len(exercise_history)

        favorite_exercises = sorted(
            exercise_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Что улучшить
        improvement_areas = self._identify_weak_points(exercises, workouts)

        return {
            'total_workouts': total_workouts,
            'total_time': total_time,
            'total_calories': total_calories,
            'current_streak': current_streak,
            'best_streak': best_streak,
            'weight_progress': weight_progress,
            'favorite_exercises': favorite_exercises,
            'improvement_areas': improvement_areas
        }

    def forecast_progress(self, user_id: int) -> Dict:
        """
        ПРОГНОЗ будущих результатов на основе текущего прогресса
        """
        history = self._load_workout_history(user_id)

        if not history or len(history.get('exercises', {})) < 3:
            return None

        exercises = history['exercises']

        # Прогнозируем для каждого упражнения
        month_forecast = {}
        quarter_forecast = {}

        for exercise_name, exercise_history in exercises.items():
            if len(exercise_history) < 5:
                continue

            # Берем последние 10 тренировок
            recent = exercise_history[-10:]
            weights = [w.get('weight', 0) for w in recent if w.get('weight', 0) > 0]

            # Рассчитываем средний прирост
            if len(weights) >= 2:
                total_growth = weights[-1] - weights[0]
                avg_growth_per_workout = total_growth / len(weights)

                # Предполагаем 12 тренировок в месяц (3 в неделю)
                month_prediction = weights[-1] + (avg_growth_per_workout * 12)
                quarter_prediction = weights[-1] + (avg_growth_per_workout * 36)

                # Реалистичные ограничения
                max_monthly_growth = weights[-1] * 0.15  # Максимум 15% в месяц
                month_prediction = min(month_prediction, weights[-1] + max_monthly_growth)
                quarter_prediction = min(quarter_prediction, weights[-1] + max_monthly_growth * 3)

                month_forecast[exercise_name] = round(month_prediction, 1)
                quarter_forecast[exercise_name] = round(quarter_prediction, 1)

        # Генерируем советы для достижения прогноза
        tips = [
            "Тренируйтесь регулярно 3-4 раза в неделю",
            "Увеличивайте веса постепенно - не более 5% за тренировку",
            "Следите за техникой - качество важнее количества",
            "Спите 7-9 часов для восстановления мышц",
            "Потребляйте 1.6-2.2г белка на кг веса тела",
            "Записывайте результаты каждой тренировки"
        ]

        return {
            'month': month_forecast,
            'quarter': quarter_forecast,
            'tips': random.sample(tips, min(3, len(tips)))
        }

    def get_training_insights(self, user_id: int) -> Dict:
        """
        ИНСАЙТЫ И СОВЕТЫ на основе глубокого анализа
        """
        history = self._load_workout_history(user_id)

        if not history or not history.get('workouts'):
            return None

        workouts = history['workouts']
        exercises = history.get('exercises', {})

        insights = {
            'patterns': [],
            'warnings': [],
            'achievements': [],
            'next_steps': []
        }

        # 1. Паттерны тренировок
        if len(workouts) >= 4:
            # Анализ времени тренировок
            workout_hours = []
            for w in workouts[-10:]:
                try:
                    hour = datetime.fromisoformat(w['date']).hour
                    workout_hours.append(hour)
                except:
                    continue

            if workout_hours:
                avg_hour = sum(workout_hours) / len(workout_hours)
                if 6 <= avg_hour < 10:
                    insights['patterns'].append("Вы предпочитаете утренние тренировки - отлично для метаболизма!")
                elif 17 <= avg_hour < 21:
                    insights['patterns'].append("Вечерние тренировки - пик физической силы!")

        # 2. Предупреждения
        recovery_status = self._assess_recovery(workouts)
        if recovery_status == 'overtraining_risk':
            insights['warnings'].append(
                "⚠️ РИСК ПЕРЕТРЕНИРОВАННОСТИ! Возьмите 2-3 дня полного отдыха"
            )

        # Проверка на долгие перерывы
        if len(workouts) >= 2:
            try:
                last_workout = datetime.fromisoformat(workouts[-1]['date'])
                days_since = (datetime.now() - last_workout).days

                if days_since > 7:
                    insights['warnings'].append(
                        f"⏰ {days_since} дней без тренировок - мышцы теряют форму!"
                    )
            except:
                pass

        # 3. Достижения
        total_workouts = len(workouts)
        milestones = [10, 25, 50, 100, 200]

        for milestone in milestones:
            if total_workouts >= milestone and total_workouts < milestone + 5:
                insights['achievements'].append(
                    f"🏆 ДОСТИЖЕНИЕ: {milestone} тренировок!"
                )

        # Проверка рекордов
        for exercise_name, exercise_history in exercises.items():
            if len(exercise_history) >= 2:
                weights = [w.get('weight', 0) for w in exercise_history if w.get('weight', 0) > 0]
                if weights and weights[-1] == max(weights):
                    insights['achievements'].append(
                        f"💪 НОВЫЙ РЕКОРД: {exercise_name} - {weights[-1]} кг!"
                    )

        # 4. Следующие шаги
        avg_progress = self.analyze_user_progress(user_id)

        if avg_progress and avg_progress.get('strength_progress'):
            progress_values = list(avg_progress['strength_progress'].values())
            if progress_values:
                avg = sum(progress_values) / len(progress_values)

                if avg < 5:
                    insights['next_steps'].append(
                        "Попробуйте новую программу или измените порядок упражнений"
                    )
                else:
                    insights['next_steps'].append(
                        "Отличный прогресс! Продолжайте увеличивать нагрузку"
                    )

        if total_workouts >= 20:
            insights['next_steps'].append(
                "Время для периодизации: чередуйте тяжелые, средние и легкие недели"
            )

        return insights


# Создаем глобальный экземпляр
workouts_loader_v4 = WorkoutsLoaderV4()


if __name__ == "__main__":
    print("=" * 80)
    print("TEST WORKOUTS LOADER V4")
    print("=" * 80)

    # Тест загрузки
    stats = workouts_loader_v4.get_stats()

    print("\nStatistika zagruzhennyh trenirovok:")
    total = 0
    for level, locations in stats.items():
        level_total = sum(sum(files.values()) for files in locations.values())
        print(f"\n{level.upper()}: {level_total} uprazhneniy")
        for location, files in locations.items():
            loc_total = sum(files.values())
            if loc_total > 0:
                print(f"  {location}: {loc_total}")
        total += level_total

    print(f"\nVSEGO: {total} uprazhneniy")

    # Тест генерации плана
    print("\n" + "=" * 80)
    print("TEST: Generatsiya plana trenirovki")
    print("=" * 80)

    plan = workouts_loader_v4.get_workout_plan_with_details(
        goal='lose_weight',
        location='gym',
        workout_type='strength',
        duration_minutes=45,
        level='intermediate'
    )

    print(f"\nGoal: {plan['goal']}")
    print(f"Location: {plan['location']}")
    print(f"Level: {plan['level']}")
    print(f"Duration: {plan['duration_minutes']} min")
    print(f"Type: {plan['type']}")
    print(f"Exercises: {plan['total_exercises']}")
    print(f"Calories: {plan['estimated_calories']} kcal")

    print("\nPervye 3 uprazhneniya:")
    for i, ex in enumerate(plan['exercises'][:3], 1):
        print(f"  {i}. {ex['Название упражнения']}")

    print("\n" + "=" * 80)
    print("[OK] Test zavershen!")
    print("=" * 80)
