"""
МЕНЕДЖЕР ИЗОБРАЖЕНИЙ
Управление и отправка изображений в Telegram боте
"""

import os
from typing import Optional, Dict
from telegram import InputMediaPhoto
import logging

logger = logging.getLogger(__name__)


class ImageManager:
    """Класс для работы с изображениями бота"""

    def __init__(self, base_path: str = "images"):
        self.base_path = base_path
        self.images: Dict[str, str] = self._scan_images()

    def _scan_images(self) -> Dict[str, str]:
        """Сканирует папку с изображениями и создает карту"""
        images = {}

        if not os.path.exists(self.base_path):
            logger.warning(f"Image folder not found: {self.base_path}")
            return images

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    # Создаем ключ из пути
                    rel_path = os.path.relpath(root, self.base_path)
                    key = f"{rel_path}/{os.path.splitext(file)[0]}".replace('\\', '/')
                    full_path = os.path.join(root, file)
                    images[key] = full_path

        logger.info(f"Loaded {len(images)} images")
        return images

    def get_image_path(self, key: str) -> Optional[str]:
        """
        Получить путь к изображению по ключу

        Args:
            key: Ключ изображения (например, 'workouts/strength')

        Returns:
            Путь к файлу или None
        """
        return self.images.get(key)

    def get_workout_image(self, workout_type: str) -> Optional[str]:
        """Получить изображение для типа тренировки"""
        workout_images = {
            'strength': 'workouts/strength',
            'cardio': 'workouts/cardio',
            'flexibility': 'workouts/flexibility',
            'full_body': 'workouts/full_body'
        }
        key = workout_images.get(workout_type)
        return self.get_image_path(key) if key else None

    def get_nutrition_image(self, meal_type: str) -> Optional[str]:
        """Получить изображение для типа питания"""
        nutrition_images = {
            'breakfast': 'nutrition/breakfast',
            'lunch': 'nutrition/lunch',
            'dinner': 'nutrition/dinner',
            'snack': 'nutrition/snack'
        }
        key = nutrition_images.get(meal_type)
        return self.get_image_path(key) if key else None

    def get_motivation_image(self, level: str = 'general') -> Optional[str]:
        """Получить мотивационное изображение"""
        return self.get_image_path(f'motivation/{level}')

    def list_available_images(self) -> Dict[str, str]:
        """Список всех доступных изображений"""
        return self.images.copy()


# Глобальный экземпляр
image_manager = ImageManager()


if __name__ == "__main__":
    # Тест
    manager = ImageManager()
    print("Доступные изображения:")
    for key, path in manager.list_available_images().items():
        print(f"  {key} -> {path}")
