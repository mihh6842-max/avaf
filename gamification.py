"""
ГЕЙМИФИКАЦИЯ И СТАТИСТИКА
Достижения, уровни, стрики, графики прогресса
"""

from database import db
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class GamificationSystem:
    """Система геймификации"""

    # Определение достижений
    ACHIEVEMENTS = {
        # Тренировки
        'first_workout': {
            'name': 'Первый шаг',
            'description': 'Выполнить первую тренировку',
            'icon': '[WORKOUT]'
        },
        'workout_5': {
            'name': 'Новичок',
            'description': '5 тренировок',
            'icon': '[POWER]'
        },
        'workout_10': {
            'name': 'Регуляр',
            'description': '10 тренировок',
            'icon': '[STAR]'
        },
        'workout_25': {
            'name': 'Любитель',
            'description': '25 тренировок',
            'icon': '[BIGSTAR]'
        },
        'workout_50': {
            'name': 'Профи',
            'description': '50 тренировок',
            'icon': '[TROPHY]'
        },
        'workout_100': {
            'name': 'Легенда',
            'description': '100 тренировок',
            'icon': '[CROWN]'
        },

        # Стрики
        'streak_3': {
            'name': 'Начало стрика',
            'description': '3 дня подряд',
            'icon': '[FIRE]'
        },
        'streak_7': {
            'name': 'Неделя!',
            'description': '7 дней подряд',
            'icon': '[FIRE]x2'
        },
        'streak_14': {
            'name': 'Две недели!',
            'description': '14 дней подряд',
            'icon': '[FIRE]x3'
        },
        'streak_30': {
            'name': 'Месяц подряд!',
            'description': '30 дней подряд',
            'icon': '[FIRE]x4'
        },

        # Калории
        'calories_1000': {
            'name': 'Жиросжигатель',
            'description': 'Сожжено 1000 ккал',
            'icon': '[BURN]'
        },
        'calories_5000': {
            'name': 'Огонь!',
            'description': 'Сожжено 5000 ккал',
            'icon': '[BURN]x2'
        },
        'calories_10000': {
            'name': 'Печка',
            'description': 'Сожжено 10000 ккал',
            'icon': '[BURN]x3'
        },

        # Особые
        'early_bird': {
            'name': 'Ранняя пташка',
            'description': 'Тренировка до 7 утра',
            'icon': '[SUNRISE]'
        },
        'night_owl': {
            'name': 'Сова',
            'description': 'Тренировка после 22:00',
            'icon': '[OWL]'
        },
        'weekend_warrior': {
            'name': 'Выходной воин',
            'description': 'Тренировка в выходной',
            'icon': '[SWORD]'
        },
    }

    def __init__(self, database=None):
        self.db = database or db

    def check_and_award_achievements(self, user_id: int) -> List[Dict]:
        """
        Проверить и выдать новые достижения

        Returns:
            Список новых достижений
        """

        new_achievements = []
        existing = self.db.get_achievements(user_id)
        existing_names = [a['achievement_name'] for a in existing]

        # Получаем статистику
        stats = self.db.get_workout_stats(user_id)
        total_workouts = stats.get('total_workouts', 0)
        total_calories = stats.get('total_calories', 0)
        current_streak = stats.get('current_streak', 0)

        # Проверяем достижения по тренировкам
        workout_achievements = {
            'first_workout': 1,
            'workout_5': 5,
            'workout_10': 10,
            'workout_25': 25,
            'workout_50': 50,
            'workout_100': 100
        }

        for ach_key, required in workout_achievements.items():
            if total_workouts >= required and ach_key not in existing_names:
                ach = self.ACHIEVEMENTS[ach_key]
                if self.db.add_achievement(user_id, 'workouts', ach_key):
                    new_achievements.append({
                        'key': ach_key,
                        'name': ach['name'],
                        'description': ach['description'],
                        'icon': ach['icon']
                    })

        # Проверяем достижения по стрикам
        streak_achievements = {
            'streak_3': 3,
            'streak_7': 7,
            'streak_14': 14,
            'streak_30': 30
        }

        for ach_key, required in streak_achievements.items():
            if current_streak >= required and ach_key not in existing_names:
                ach = self.ACHIEVEMENTS[ach_key]
                if self.db.add_achievement(user_id, 'streak', ach_key):
                    new_achievements.append({
                        'key': ach_key,
                        'name': ach['name'],
                        'description': ach['description'],
                        'icon': ach['icon']
                    })

        # Проверяем достижения по калориям
        calories_achievements = {
            'calories_1000': 1000,
            'calories_5000': 5000,
            'calories_10000': 10000
        }

        for ach_key, required in calories_achievements.items():
            if total_calories >= required and ach_key not in existing_names:
                ach = self.ACHIEVEMENTS[ach_key]
                if self.db.add_achievement(user_id, 'calories', ach_key):
                    new_achievements.append({
                        'key': ach_key,
                        'name': ach['name'],
                        'description': ach['description'],
                        'icon': ach['icon']
                    })

        return new_achievements

    def get_user_level(self, user_id: int) -> Dict:
        """
        Определить уровень пользователя

        Returns:
            {
                'level': int,
                'level_name': str,
                'current_xp': int,
                'next_level_xp': int,
                'progress_percent': float
            }
        """

        stats = self.db.get_workout_stats(user_id)
        total_workouts = stats.get('total_workouts', 0)

        # XP: 1 тренировка = 100 XP
        current_xp = total_workouts * 100

        # Уровни:
        # Уровень 1: 0-499 XP
        # Уровень 2: 500-999 XP
        # Уровень 3: 1000-1999 XP
        # и так далее

        level = 1
        xp_for_level = 500

        while current_xp >= xp_for_level:
            level += 1
            xp_for_level += 500

        # XP для следующего уровня
        xp_for_current_level = (level - 1) * 500 if level > 1 else 0
        xp_for_next_level = level * 500

        progress = ((current_xp - xp_for_current_level) /
                   (xp_for_next_level - xp_for_current_level)) * 100

        # Названия уровней
        level_names = {
            1: 'Новичок',
            2: 'Ученик',
            3: 'Любитель',
            4: 'Энтузиаст',
            5: 'Спортсмен',
            6: 'Профессионал',
            7: 'Эксперт',
            8: 'Мастер',
            9: 'Гуру',
            10: 'Легенда'
        }

        level_name = level_names.get(level, f'Уровень {level}')

        return {
            'level': level,
            'level_name': level_name,
            'current_xp': current_xp,
            'xp_for_current_level': xp_for_current_level,
            'xp_for_next_level': xp_for_next_level,
            'progress_percent': round(progress, 1)
        }

    def format_achievements_message(self, user_id: int) -> str:
        """Форматировать сообщение с достижениями"""

        achievements = self.db.get_achievements(user_id)
        level_info = self.get_user_level(user_id)

        if not achievements:
            return "У вас пока нет достижений. Начните тренироваться!"

        message = f"Ваш уровень: {level_info['level']} - {level_info['level_name']}\n"
        message += f"XP: {level_info['current_xp']}/{level_info['xp_for_next_level']}\n\n"
        message += f"Ваши достижения ({len(achievements)}):\n\n"

        for ach in achievements:
            ach_key = ach['achievement_name']
            ach_info = self.ACHIEVEMENTS.get(ach_key, {})
            icon = ach_info.get('icon', '')
            name = ach_info.get('name', ach_key)
            desc = ach_info.get('description', '')

            message += f"{icon} {name}\n"
            message += f"   {desc}\n\n"

        return message


class StatisticsSystem:
    """Система статистики и прогресса"""

    def __init__(self, database=None):
        self.db = database or db

    def get_workout_summary(self, user_id: int, days: int = 30) -> Dict:
        """Сводка по тренировкам за период"""

        history = self.db.get_workout_history(user_id, days)

        if not history:
            return {'no_data': True}

        total_workouts = len(history)
        total_minutes = sum(w['duration_minutes'] or 0 for w in history)
        total_calories = sum(w['calories_burned'] or 0 for w in history)

        # Группируем по типам
        by_type = {}
        for workout in history:
            wtype = workout['workout_type']
            by_type[wtype] = by_type.get(wtype, 0) + 1

        return {
            'period_days': days,
            'total_workouts': total_workouts,
            'total_minutes': total_minutes,
            'total_hours': round(total_minutes / 60, 1),
            'total_calories': total_calories,
            'avg_duration': round(total_minutes / total_workouts, 1) if total_workouts > 0 else 0,
            'by_type': by_type,
            'workouts_per_week': round((total_workouts / days) * 7, 1)
        }

    def get_weight_progress(self, user_id: int, days: int = 90) -> Dict:
        """Прогресс по весу"""

        measurements = self.db.get_measurements(user_id, days)

        if not measurements:
            return {'no_data': True}

        weights = [(m['measurement_date'], m['weight']) for m in measurements if m['weight']]
        weights.sort(key=lambda x: x[0])

        if len(weights) < 2:
            return {'not_enough_data': True}

        first_date, first_weight = weights[0]
        last_date, last_weight = weights[-1]

        change = last_weight - first_weight
        change_percent = (change / first_weight) * 100 if first_weight > 0 else 0

        return {
            'first_weight': first_weight,
            'last_weight': last_weight,
            'change_kg': round(change, 1),
            'change_percent': round(change_percent, 1),
            'measurements_count': len(weights),
            'period_days': (datetime.strptime(last_date, '%Y-%m-%d') -
                          datetime.strptime(first_date, '%Y-%m-%d')).days
        }

    def format_statistics_message(self, user_id: int) -> str:
        """Форматировать сообщение со статистикой"""

        # Статистика тренировок
        stats_week = self.get_workout_summary(user_id, 7)
        stats_month = self.get_workout_summary(user_id, 30)

        message = "СТАТИСТИКА ТРЕНИРОВОК\n\n"

        if not stats_week.get('no_data'):
            message += "За последнюю неделю:\n"
            message += f"  Тренировок: {stats_week['total_workouts']}\n"
            message += f"  Время: {stats_week['total_hours']} часов\n"
            message += f"  Сожжено: {stats_week['total_calories']} ккал\n\n"

        if not stats_month.get('no_data'):
            message += "За последний месяц:\n"
            message += f"  Тренировок: {stats_month['total_workouts']}\n"
            message += f"  Время: {stats_month['total_hours']} часов\n"
            message += f"  Сожжено: {stats_month['total_calories']} ккал\n"
            message += f"  Средняя длительность: {stats_month['avg_duration']} мин\n\n"

            if stats_month['by_type']:
                message += "По типам:\n"
                for wtype, count in stats_month['by_type'].items():
                    message += f"  {wtype}: {count}\n"

        # Прогресс по весу
        weight_progress = self.get_weight_progress(user_id)

        if not weight_progress.get('no_data') and not weight_progress.get('not_enough_data'):
            message += "\nПРОГРЕСС ПО ВЕСУ:\n"
            message += f"  Было: {weight_progress['first_weight']} кг\n"
            message += f"  Стало: {weight_progress['last_weight']} кг\n"
            message += f"  Изменение: {weight_progress['change_kg']:+.1f} кг "
            message += f"({weight_progress['change_percent']:+.1f}%)\n"

        return message


# Создаем глобальные экземпляры
gamification = GamificationSystem()
statistics = StatisticsSystem()


if __name__ == "__main__":
    # Тест системы геймификации

    print("=" * 80)
    print("ТЕСТ ГЕЙМИФИКАЦИИ И СТАТИСТИКИ")
    print("=" * 80)

    # Создаем тестового пользователя
    user_id = 99999

    try:
        db.create_user(user_id, "Тест Геймификации", "lose_weight", "home")
    except:
        pass

    # Добавляем тренировки
    from datetime import date

    for i in range(7):
        workout_date = (date.today() - timedelta(days=i)).strftime('%Y-%m-%d')
        db.add_workout(
            user_id=user_id,
            workout_date=workout_date,
            workout_type='strength',
            duration_minutes=45,
            calories_burned=300,
            exercises_count=10,
            workout_data={}
        )

    # Проверяем достижения
    print("\nПроверка достижений...")
    new_achievements = gamification.check_and_award_achievements(user_id)

    if new_achievements:
        print(f"Получено новых достижений: {len(new_achievements)}")
        for ach in new_achievements:
            print(f"  {ach['icon']} {ach['name']} - {ach['description']}")
    else:
        print("Новых достижений нет")

    # Проверяем уровень
    print("\nИнформация об уровне:")
    level_info = gamification.get_user_level(user_id)
    print(f"  Уровень: {level_info['level']} - {level_info['level_name']}")
    print(f"  XP: {level_info['current_xp']}/{level_info['xp_for_next_level']}")
    print(f"  Прогресс: {level_info['progress_percent']}%")

    # Статистика
    print("\nСтатистика тренировок:")
    summary = statistics.get_workout_summary(user_id, 7)
    print(f"  Тренировок за неделю: {summary['total_workouts']}")
    print(f"  Всего времени: {summary['total_hours']} часов")
    print(f"  Сожжено калорий: {summary['total_calories']}")

    # Добавляем замеры
    db.add_measurement(
        user_id=user_id,
        measurement_date=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
        weight=80.0
    )
    db.add_measurement(
        user_id=user_id,
        measurement_date=date.today().strftime('%Y-%m-%d'),
        weight=77.5
    )

    # Прогресс по весу
    print("\nПрогресс по весу:")
    weight_prog = statistics.get_weight_progress(user_id)
    if not weight_prog.get('no_data'):
        print(f"  Было: {weight_prog['first_weight']} кг")
        print(f"  Стало: {weight_prog['last_weight']} кг")
        print(f"  Изменение: {weight_prog['change_kg']} кг ({weight_prog['change_percent']}%)")

    print("\n" + "=" * 80)
    print("[OK] Геймификация и статистика работают!")
    print("=" * 80)
