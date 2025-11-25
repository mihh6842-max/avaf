"""
СИСТЕМА БАЗЫ ДАННЫХ
SQLite для хранения профилей, истории, предпочтений
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class Database:
    """Управление базой данных"""

    def __init__(self, db_path='fitness_bot.db'):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def connect(self):
        """Подключение к БД"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_database(self):
        """Инициализация таблиц"""
        conn = self.connect()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                goal TEXT NOT NULL,
                location TEXT NOT NULL,
                level TEXT DEFAULT 'intermediate',
                weight REAL,
                height REAL,
                age INTEGER,
                gender TEXT,
                activity_level TEXT,
                daily_calories INTEGER,
                daily_protein INTEGER,
                daily_fats INTEGER,
                daily_carbs INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица предпочтений в питании
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_type TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, preference_type, value)
            )
        ''')

        # Таблица истории тренировок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                workout_date DATE NOT NULL,
                workout_type TEXT NOT NULL,
                duration_minutes INTEGER,
                calories_burned INTEGER,
                exercises_count INTEGER,
                workout_data TEXT,
                completed BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица истории питания
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                meal_name TEXT,
                calories INTEGER,
                protein INTEGER,
                fats INTEGER,
                carbs INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица достижений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица стриков (дни подряд)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaks (
                user_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_workout_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Таблица замеров (вес, объемы)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                measurement_date DATE NOT NULL,
                weight REAL,
                chest REAL,
                waist REAL,
                hips REAL,
                biceps REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()

    # === РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ===

    def create_user(self, user_id: int, name: str, goal: str, location: str,
                    level: str = 'intermediate', **kwargs) -> bool:
        """Создать нового пользователя"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (user_id, name, goal, location, level,
                                 weight, height, age, gender, activity_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, goal, location, level,
                  kwargs.get('weight'), kwargs.get('height'),
                  kwargs.get('age'), kwargs.get('gender'),
                  kwargs.get('activity_level')))

            # Инициализируем стрик
            cursor.execute('''
                INSERT INTO streaks (user_id, current_streak, longest_streak)
                VALUES (?, 0, 0)
            ''', (user_id,))

            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя"""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"[ERROR] Database error in get_user({user_id}): {e}")
            return None
        except Exception as e:
            print(f"[CRITICAL] Unexpected error in get_user({user_id}): {e}")
            return None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновить данные пользователя"""
        try:
            conn = self.connect()
            cursor = conn.cursor()

            fields = []
            values = []

            for key, value in kwargs.items():
                if value is not None:
                    fields.append(f"{key} = ?")
                    values.append(value)

            if not fields:
                return False

            fields.append("last_active = CURRENT_TIMESTAMP")
            values.append(user_id)

            query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[ERROR] Database error in update_user({user_id}): {e}")
            return False
        except Exception as e:
            print(f"[CRITICAL] Unexpected error in update_user({user_id}): {e}")
            return False

    # === ПРЕДПОЧТЕНИЯ В ПИТАНИИ ===

    def add_food_preference(self, user_id: int, preference_type: str, value: str) -> bool:
        """Добавить предпочтение (аллергия, исключение)"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO food_preferences (user_id, preference_type, value)
                VALUES (?, ?, ?)
            ''', (user_id, preference_type, value))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_food_preferences(self, user_id: int) -> Dict[str, List[str]]:
        """Получить все предпочтения пользователя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT preference_type, value FROM food_preferences
            WHERE user_id = ?
        ''', (user_id,))

        preferences = {}
        for row in cursor.fetchall():
            pref_type = row['preference_type']
            value = row['value']

            if pref_type not in preferences:
                preferences[pref_type] = []
            preferences[pref_type].append(value)

        return preferences

    def remove_food_preference(self, user_id: int, preference_type: str, value: str) -> bool:
        """Удалить предпочтение"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM food_preferences
            WHERE user_id = ? AND preference_type = ? AND value = ?
        ''', (user_id, preference_type, value))
        conn.commit()

        return cursor.rowcount > 0

    # === ИСТОРИЯ ТРЕНИРОВОК ===

    def add_workout(self, user_id: int, workout_date: str, workout_type: str,
                   duration_minutes: int, calories_burned: int,
                   exercises_count: int, workout_data: dict) -> int:
        """Добавить выполненную тренировку"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO workout_history
            (user_id, workout_date, workout_type, duration_minutes,
             calories_burned, exercises_count, workout_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, workout_date, workout_type, duration_minutes,
              calories_burned, exercises_count, json.dumps(workout_data)))

        conn.commit()

        # Обновляем стрик
        self._update_streak(user_id, workout_date)

        return cursor.lastrowid

    def get_workout_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Получить историю тренировок"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM workout_history
            WHERE user_id = ?
            AND workout_date >= date('now', '-' || ? || ' days')
            ORDER BY workout_date DESC
        ''', (user_id, days))

        return [dict(row) for row in cursor.fetchall()]

    def get_workout_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику тренировок"""
        conn = self.connect()
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute('''
            SELECT
                COUNT(*) as total_workouts,
                SUM(duration_minutes) as total_minutes,
                SUM(calories_burned) as total_calories,
                AVG(duration_minutes) as avg_duration
            FROM workout_history
            WHERE user_id = ?
        ''', (user_id,))

        stats = dict(cursor.fetchone())

        # За последние 7 дней
        cursor.execute('''
            SELECT COUNT(*) as workouts_this_week
            FROM workout_history
            WHERE user_id = ?
            AND workout_date >= date('now', '-7 days')
        ''', (user_id,))

        stats.update(dict(cursor.fetchone()))

        # Стрик
        cursor.execute('SELECT * FROM streaks WHERE user_id = ?', (user_id,))
        streak_row = cursor.fetchone()
        if streak_row:
            stats.update(dict(streak_row))

        return stats

    def _update_streak(self, user_id: int, workout_date: str):
        """Обновить стрик пользователя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM streaks WHERE user_id = ?', (user_id,))
        streak = cursor.fetchone()

        if not streak:
            return

        current_streak = streak['current_streak']
        longest_streak = streak['longest_streak']
        last_date = streak['last_workout_date']

        workout_dt = datetime.strptime(workout_date, '%Y-%m-%d').date()

        if last_date:
            last_dt = datetime.strptime(last_date, '%Y-%m-%d').date()
            diff = (workout_dt - last_dt).days

            if diff == 1:
                # Продолжаем стрик
                current_streak += 1
            elif diff == 0:
                # Та же дата, стрик не меняется
                pass
            else:
                # Стрик прерван
                current_streak = 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

        cursor.execute('''
            UPDATE streaks
            SET current_streak = ?, longest_streak = ?, last_workout_date = ?
            WHERE user_id = ?
        ''', (current_streak, longest_streak, workout_date, user_id))

        conn.commit()

    # === ИСТОРИЯ ПИТАНИЯ ===

    def add_meal(self, user_id: int, meal_date: str, meal_type: str,
                meal_name: str, calories: int, protein: int, fats: int, carbs: int) -> int:
        """Добавить прием пищи"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO meal_history
            (user_id, meal_date, meal_type, meal_name, calories, protein, fats, carbs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_date, meal_type, meal_name, calories, protein, fats, carbs))

        conn.commit()
        return cursor.lastrowid

    def get_meal_history(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Получить историю питания"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM meal_history
            WHERE user_id = ?
            AND meal_date >= date('now', '-' || ? || ' days')
            ORDER BY meal_date DESC, created_at DESC
        ''', (user_id, days))

        return [dict(row) for row in cursor.fetchall()]

    # === ДОСТИЖЕНИЯ ===

    def add_achievement(self, user_id: int, achievement_type: str, achievement_name: str) -> bool:
        """Добавить достижение"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO achievements (user_id, achievement_type, achievement_name)
                VALUES (?, ?, ?)
            ''', (user_id, achievement_type, achievement_name))
            conn.commit()
            return True
        except:
            return False

    def get_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все достижения пользователя"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM achievements
            WHERE user_id = ?
            ORDER BY earned_at DESC
        ''', (user_id,))

        return [dict(row) for row in cursor.fetchall()]

    # === ЗАМЕРЫ ===

    def add_measurement(self, user_id: int, measurement_date: str, **kwargs) -> int:
        """Добавить замер"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO measurements
            (user_id, measurement_date, weight, chest, waist, hips, biceps, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, measurement_date,
              kwargs.get('weight'), kwargs.get('chest'),
              kwargs.get('waist'), kwargs.get('hips'),
              kwargs.get('biceps'), kwargs.get('notes')))

        conn.commit()
        return cursor.lastrowid

    def get_measurements(self, user_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """Получить историю замеров"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM measurements
            WHERE user_id = ?
            AND measurement_date >= date('now', '-' || ? || ' days')
            ORDER BY measurement_date DESC
        ''', (user_id, days))

        return [dict(row) for row in cursor.fetchall()]


# Создаем глобальный экземпляр
db = Database()


if __name__ == "__main__":
    # Тест базы данных
    print("Инициализация БД...")

    # Создаем тестового пользователя
    user_id = 12345
    db.create_user(
        user_id=user_id,
        name="Тест",
        goal="gain_weight",
        location="gym",
        level="intermediate",
        weight=75.0,
        height=180,
        age=25,
        gender="male",
        activity_level="moderate"
    )

    # Получаем пользователя
    user = db.get_user(user_id)
    print(f"\nПользователь создан: {user['name']}")

    # Добавляем предпочтения
    db.add_food_preference(user_id, 'allergy', 'лактоза')
    db.add_food_preference(user_id, 'exclude', 'свинина')

    prefs = db.get_food_preferences(user_id)
    print(f"Предпочтения: {prefs}")

    # Добавляем тренировку
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')

    db.add_workout(
        user_id=user_id,
        workout_date=today,
        workout_type='strength',
        duration_minutes=45,
        calories_burned=300,
        exercises_count=10,
        workout_data={'exercises': ['Жим', 'Присед']}
    )

    # Статистика
    stats = db.get_workout_stats(user_id)
    print(f"\nСтатистика: {stats}")

    print("\n[OK] База данных работает!")
