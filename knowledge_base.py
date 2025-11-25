"""
База знаний для AI-системы генерации планов питания и тренировок
Содержит полную информацию о продуктах, рецептах и упражнениях
"""

from typing import Dict, List, Optional
from recipes_loader import recipes_loader


class NutritionDatabase:
    """База данных продуктов с полной информацией"""

    PRODUCTS = {
        # БЕЛКОВЫЕ ПРОДУКТЫ
        "куриная_грудка": {
            "name_ru": "Куриная грудка",
            "name_en": "Chicken breast",
            "name_uz": "Tovuq ko'kragi",
            "calories_per_100g": 165,
            "protein_per_100g": 31.0,
            "fat_per_100g": 3.6,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["grill", "bake", "boil", "fry"],
            "cooking_time_minutes": 15,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 2
        },
        "говядина": {
            "name_ru": "Говядина постная",
            "name_en": "Lean beef",
            "name_uz": "Mol go'shti",
            "calories_per_100g": 250,
            "protein_per_100g": 26.0,
            "fat_per_100g": 15.0,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["grill", "bake", "fry", "stew"],
            "cooking_time_minutes": 25,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 2
        },
        "рыба_треска": {
            "name_ru": "Треска",
            "name_en": "Cod fish",
            "name_uz": "Treska baliq",
            "calories_per_100g": 82,
            "protein_per_100g": 17.0,
            "fat_per_100g": 0.7,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["bake", "steam", "fry"],
            "cooking_time_minutes": 12,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 1
        },
        "лосось": {
            "name_ru": "Лосось",
            "name_en": "Salmon",
            "name_uz": "Losos baliq",
            "calories_per_100g": 208,
            "protein_per_100g": 20.0,
            "fat_per_100g": 13.0,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["bake", "grill", "steam"],
            "cooking_time_minutes": 15,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 1
        },
        "яйца": {
            "name_ru": "Куриные яйца",
            "name_en": "Chicken eggs",
            "name_uz": "Tovuq tuxumlari",
            "calories_per_100g": 155,
            "protein_per_100g": 13.0,
            "fat_per_100g": 11.0,
            "carbs_per_100g": 1.1,
            "category": "protein",
            "cooking_methods": ["boil", "fry", "scramble"],
            "cooking_time_minutes": 5,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 14
        },
        "творог": {
            "name_ru": "Творог обезжиренный",
            "name_en": "Low-fat cottage cheese",
            "name_uz": "Tvorog (yog'siz)",
            "calories_per_100g": 72,
            "protein_per_100g": 16.0,
            "fat_per_100g": 0.5,
            "carbs_per_100g": 3.3,
            "category": "protein",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 5
        },
        "греческий_йогурт": {
            "name_ru": "Греческий йогурт",
            "name_en": "Greek yogurt",
            "name_uz": "Yunon yogurti",
            "calories_per_100g": 59,
            "protein_per_100g": 10.0,
            "fat_per_100g": 0.4,
            "carbs_per_100g": 3.6,
            "category": "protein",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 7
        },
        "индейка": {
            "name_ru": "Филе индейки",
            "name_en": "Turkey breast",
            "name_uz": "Kurka go'shti",
            "calories_per_100g": 157,
            "protein_per_100g": 30.0,
            "fat_per_100g": 3.2,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["bake", "grill", "boil"],
            "cooking_time_minutes": 18,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 2
        },

        # УГЛЕВОДЫ
        "рис_белый": {
            "name_ru": "Рис белый (варёный)",
            "name_en": "White rice (cooked)",
            "name_uz": "Oq guruch (pishirilgan)",
            "calories_per_100g": 130,
            "protein_per_100g": 2.7,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 28.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 20,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },
        "рис_бурый": {
            "name_ru": "Рис бурый (варёный)",
            "name_en": "Brown rice (cooked)",
            "name_uz": "Jigarrang guruch (pishirilgan)",
            "calories_per_100g": 111,
            "protein_per_100g": 2.6,
            "fat_per_100g": 0.9,
            "carbs_per_100g": 23.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 35,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 180
        },
        "гречка": {
            "name_ru": "Гречка (варёная)",
            "name_en": "Buckwheat (cooked)",
            "name_uz": "Grechka (pishirilgan)",
            "calories_per_100g": 92,
            "protein_per_100g": 3.4,
            "fat_per_100g": 0.6,
            "carbs_per_100g": 18.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 15,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },
        "овсянка": {
            "name_ru": "Овсяные хлопья (сухие)",
            "name_en": "Oatmeal (dry)",
            "name_uz": "Jo'xori (quruq)",
            "calories_per_100g": 389,
            "protein_per_100g": 16.9,
            "fat_per_100g": 6.9,
            "carbs_per_100g": 66.3,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 5,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },
        "макароны": {
            "name_ru": "Макароны из твёрдых сортов (варёные)",
            "name_en": "Whole wheat pasta (cooked)",
            "name_uz": "Makaron (pishirilgan)",
            "calories_per_100g": 157,
            "protein_per_100g": 5.5,
            "fat_per_100g": 0.9,
            "carbs_per_100g": 31.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 10,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 730
        },
        "картофель": {
            "name_ru": "Картофель (варёный)",
            "name_en": "Potato (boiled)",
            "name_uz": "Kartoshka (pishirilgan)",
            "calories_per_100g": 86,
            "protein_per_100g": 2.0,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 20.0,
            "category": "carbs",
            "cooking_methods": ["boil", "bake", "fry"],
            "cooking_time_minutes": 25,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 30
        },
        "батат": {
            "name_ru": "Батат (запечённый)",
            "name_en": "Sweet potato (baked)",
            "name_uz": "Shirin kartoshka",
            "calories_per_100g": 90,
            "protein_per_100g": 2.0,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 21.0,
            "category": "carbs",
            "cooking_methods": ["bake", "boil"],
            "cooking_time_minutes": 30,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 21
        },
        "киноа": {
            "name_ru": "Киноа (варёная)",
            "name_en": "Quinoa (cooked)",
            "name_uz": "Kinoa (pishirilgan)",
            "calories_per_100g": 120,
            "protein_per_100g": 4.4,
            "fat_per_100g": 1.9,
            "carbs_per_100g": 21.3,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 15,
            "price_tier": "high",
            "availability": "low",
            "shelf_life_days": 365
        },
        "хлеб_цельнозерновой": {
            "name_ru": "Цельнозерновой хлеб",
            "name_en": "Whole grain bread",
            "name_uz": "To'liq donli non",
            "calories_per_100g": 247,
            "protein_per_100g": 9.0,
            "fat_per_100g": 3.5,
            "carbs_per_100g": 41.0,
            "category": "carbs",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 7
        },

        # ОВОЩИ
        "брокколи": {
            "name_ru": "Брокколи",
            "name_en": "Broccoli",
            "name_uz": "Brokkoli",
            "calories_per_100g": 34,
            "protein_per_100g": 2.8,
            "fat_per_100g": 0.4,
            "carbs_per_100g": 7.0,
            "category": "vegetables",
            "cooking_methods": ["steam", "boil", "fry"],
            "cooking_time_minutes": 5,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 5
        },
        "шпинат": {
            "name_ru": "Шпинат",
            "name_en": "Spinach",
            "name_uz": "Ismaloq",
            "calories_per_100g": 23,
            "protein_per_100g": 2.9,
            "fat_per_100g": 0.4,
            "carbs_per_100g": 3.6,
            "category": "vegetables",
            "cooking_methods": ["raw", "steam", "fry"],
            "cooking_time_minutes": 2,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 3
        },
        "помидоры": {
            "name_ru": "Помидоры",
            "name_en": "Tomatoes",
            "name_uz": "Pomidor",
            "calories_per_100g": 18,
            "protein_per_100g": 0.9,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 3.9,
            "category": "vegetables",
            "cooking_methods": ["raw", "bake", "fry"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 7
        },
        "огурцы": {
            "name_ru": "Огурцы",
            "name_en": "Cucumbers",
            "name_uz": "Bodring",
            "calories_per_100g": 15,
            "protein_per_100g": 0.7,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 3.6,
            "category": "vegetables",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 7
        },
        "морковь": {
            "name_ru": "Морковь",
            "name_en": "Carrots",
            "name_uz": "Sabzi",
            "calories_per_100g": 41,
            "protein_per_100g": 0.9,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 10.0,
            "category": "vegetables",
            "cooking_methods": ["raw", "boil", "steam"],
            "cooking_time_minutes": 10,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 30
        },
        "болгарский_перец": {
            "name_ru": "Болгарский перец",
            "name_en": "Bell pepper",
            "name_uz": "Bulg'or qalampiri",
            "calories_per_100g": 27,
            "protein_per_100g": 1.0,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 6.0,
            "category": "vegetables",
            "cooking_methods": ["raw", "fry", "bake"],
            "cooking_time_minutes": 5,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 10
        },
        "кабачок": {
            "name_ru": "Кабачок",
            "name_en": "Zucchini",
            "name_uz": "Qovoq",
            "calories_per_100g": 17,
            "protein_per_100g": 1.2,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 3.1,
            "category": "vegetables",
            "cooking_methods": ["fry", "bake", "steam"],
            "cooking_time_minutes": 8,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 7
        },
        "капуста": {
            "name_ru": "Белокочанная капуста",
            "name_en": "Cabbage",
            "name_uz": "Karam",
            "calories_per_100g": 25,
            "protein_per_100g": 1.3,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 5.8,
            "category": "vegetables",
            "cooking_methods": ["raw", "boil", "fry", "stew"],
            "cooking_time_minutes": 10,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 30
        },
        "салат": {
            "name_ru": "Салат листовой",
            "name_en": "Lettuce",
            "name_uz": "Salat bargi",
            "calories_per_100g": 15,
            "protein_per_100g": 1.4,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 2.9,
            "category": "vegetables",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 3
        },
        "спаржа": {
            "name_ru": "Спаржа",
            "name_en": "Asparagus",
            "name_uz": "Qushqo'nmas",
            "calories_per_100g": 20,
            "protein_per_100g": 2.2,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 3.9,
            "category": "vegetables",
            "cooking_methods": ["steam", "grill", "bake"],
            "cooking_time_minutes": 7,
            "price_tier": "high",
            "availability": "low",
            "shelf_life_days": 3
        },

        # ФРУКТЫ
        "яблоко": {
            "name_ru": "Яблоко",
            "name_en": "Apple",
            "name_uz": "Olma",
            "calories_per_100g": 52,
            "protein_per_100g": 0.3,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 14.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 30
        },
        "банан": {
            "name_ru": "Банан",
            "name_en": "Banana",
            "name_uz": "Banan",
            "calories_per_100g": 89,
            "protein_per_100g": 1.1,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 23.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 7
        },
        "ягоды": {
            "name_ru": "Ягоды (черника/клубника)",
            "name_en": "Berries (blueberries/strawberries)",
            "name_uz": "Mevalar (qora rezavor/qulupnay)",
            "calories_per_100g": 57,
            "protein_per_100g": 0.7,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 14.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 3
        },
        "апельсин": {
            "name_ru": "Апельсин",
            "name_en": "Orange",
            "name_uz": "Apelsin",
            "calories_per_100g": 47,
            "protein_per_100g": 0.9,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 12.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 14
        },
        "груша": {
            "name_ru": "Груша",
            "name_en": "Pear",
            "name_uz": "Nok",
            "calories_per_100g": 57,
            "protein_per_100g": 0.4,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 15.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 21
        },

        # ЖИРЫ И ОРЕХИ
        "авокадо": {
            "name_ru": "Авокадо",
            "name_en": "Avocado",
            "name_uz": "Avokado",
            "calories_per_100g": 160,
            "protein_per_100g": 2.0,
            "fat_per_100g": 15.0,
            "carbs_per_100g": 9.0,
            "category": "fats",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 5
        },
        "грецкие_орехи": {
            "name_ru": "Грецкие орехи",
            "name_en": "Walnuts",
            "name_uz": "Yong'oq",
            "calories_per_100g": 654,
            "protein_per_100g": 15.0,
            "fat_per_100g": 65.0,
            "carbs_per_100g": 14.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 180
        },
        "миндаль": {
            "name_ru": "Миндаль",
            "name_en": "Almonds",
            "name_uz": "Bodom",
            "calories_per_100g": 579,
            "protein_per_100g": 21.0,
            "fat_per_100g": 50.0,
            "carbs_per_100g": 22.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 180
        },
        "арахис": {
            "name_ru": "Арахис",
            "name_en": "Peanuts",
            "name_uz": "Yer yong'og'i",
            "calories_per_100g": 567,
            "protein_per_100g": 26.0,
            "fat_per_100g": 49.0,
            "carbs_per_100g": 16.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 180
        },
        "оливковое_масло": {
            "name_ru": "Оливковое масло",
            "name_en": "Olive oil",
            "name_uz": "Zaytun moyi",
            "calories_per_100g": 884,
            "protein_per_100g": 0.0,
            "fat_per_100g": 100.0,
            "carbs_per_100g": 0.0,
            "category": "fats",
            "cooking_methods": ["raw", "fry"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 730
        },

        # МОЛОЧНЫЕ ПРОДУКТЫ
        "молоко": {
            "name_ru": "Молоко 2.5%",
            "name_en": "Milk 2.5%",
            "name_uz": "Sut 2.5%",
            "calories_per_100g": 52,
            "protein_per_100g": 3.2,
            "fat_per_100g": 2.5,
            "carbs_per_100g": 4.7,
            "category": "dairy",
            "cooking_methods": ["raw", "boil"],
            "cooking_time_minutes": 0,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 5
        },
        "сыр_моцарелла": {
            "name_ru": "Сыр моцарелла",
            "name_en": "Mozzarella cheese",
            "name_uz": "Motsarella pishloq",
            "calories_per_100g": 280,
            "protein_per_100g": 28.0,
            "fat_per_100g": 17.0,
            "carbs_per_100g": 3.0,
            "category": "dairy",
            "cooking_methods": ["raw", "bake"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 14
        },

        # ДОПОЛНИТЕЛЬНЫЕ
        "мед": {
            "name_ru": "Мёд",
            "name_en": "Honey",
            "name_uz": "Asal",
            "calories_per_100g": 304,
            "protein_per_100g": 0.3,
            "fat_per_100g": 0.0,
            "carbs_per_100g": 82.0,
            "category": "sweeteners",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 730
        },

        # ДОПОЛНИТЕЛЬНЫЕ БЕЛКОВЫЕ ПРОДУКТЫ
        "тунец": {
            "name_ru": "Тунец консервированный",
            "name_en": "Canned tuna",
            "name_uz": "Konservalangan tuna",
            "calories_per_100g": 116,
            "protein_per_100g": 26.0,
            "fat_per_100g": 1.0,
            "carbs_per_100g": 0.0,
            "category": "protein",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 730
        },
        "креветки": {
            "name_ru": "Креветки",
            "name_en": "Shrimp",
            "name_uz": "Qisqichbaqa",
            "calories_per_100g": 99,
            "protein_per_100g": 24.0,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 0.2,
            "category": "protein",
            "cooking_methods": ["boil", "fry", "grill"],
            "cooking_time_minutes": 5,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 1
        },
        "тофу": {
            "name_ru": "Тофу",
            "name_en": "Tofu",
            "name_uz": "Tofu",
            "calories_per_100g": 76,
            "protein_per_100g": 8.0,
            "fat_per_100g": 4.8,
            "carbs_per_100g": 1.9,
            "category": "protein",
            "cooking_methods": ["fry", "bake", "raw"],
            "cooking_time_minutes": 10,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 7
        },
        "протеин_порошок": {
            "name_ru": "Протеиновый порошок",
            "name_en": "Protein powder",
            "name_uz": "Protein kukuni",
            "calories_per_100g": 400,
            "protein_per_100g": 80.0,
            "fat_per_100g": 5.0,
            "carbs_per_100g": 10.0,
            "category": "protein",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 365
        },

        # БОЛЬШЕ УГЛЕВОДОВ
        "кускус": {
            "name_ru": "Кускус (варёный)",
            "name_en": "Couscous (cooked)",
            "name_uz": "Kuskus (pishirilgan)",
            "calories_per_100g": 112,
            "protein_per_100g": 3.8,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 23.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 5,
            "price_tier": "medium",
            "availability": "medium",
            "shelf_life_days": 365
        },
        "чечевица": {
            "name_ru": "Чечевица (варёная)",
            "name_en": "Lentils (cooked)",
            "name_uz": "Yasmiq (pishirilgan)",
            "calories_per_100g": 116,
            "protein_per_100g": 9.0,
            "fat_per_100g": 0.4,
            "carbs_per_100g": 20.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 25,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },
        "фасоль": {
            "name_ru": "Фасоль красная (варёная)",
            "name_en": "Red beans (cooked)",
            "name_uz": "Qizil loviya (pishirilgan)",
            "calories_per_100g": 127,
            "protein_per_100g": 8.7,
            "fat_per_100g": 0.5,
            "carbs_per_100g": 23.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 60,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },
        "нут": {
            "name_ru": "Нут (варёный)",
            "name_en": "Chickpeas (cooked)",
            "name_uz": "No'xat (pishirilgan)",
            "calories_per_100g": 164,
            "protein_per_100g": 8.9,
            "fat_per_100g": 2.6,
            "carbs_per_100g": 27.0,
            "category": "carbs",
            "cooking_methods": ["boil"],
            "cooking_time_minutes": 45,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 365
        },

        # БОЛЬШЕ ОВОЩЕЙ
        "цветная_капуста": {
            "name_ru": "Цветная капуста",
            "name_en": "Cauliflower",
            "name_uz": "Gulkaram",
            "calories_per_100g": 25,
            "protein_per_100g": 1.9,
            "fat_per_100g": 0.3,
            "carbs_per_100g": 5.0,
            "category": "vegetables",
            "cooking_methods": ["steam", "boil", "bake", "fry"],
            "cooking_time_minutes": 8,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 7
        },
        "баклажан": {
            "name_ru": "Баклажан",
            "name_en": "Eggplant",
            "name_uz": "Baqlajon",
            "calories_per_100g": 25,
            "protein_per_100g": 1.0,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 6.0,
            "category": "vegetables",
            "cooking_methods": ["fry", "bake", "grill"],
            "cooking_time_minutes": 15,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 7
        },
        "стручковая_фасоль": {
            "name_ru": "Стручковая фасоль",
            "name_en": "Green beans",
            "name_uz": "Yashil loviya",
            "calories_per_100g": 31,
            "protein_per_100g": 1.8,
            "fat_per_100g": 0.2,
            "carbs_per_100g": 7.0,
            "category": "vegetables",
            "cooking_methods": ["steam", "boil", "fry"],
            "cooking_time_minutes": 7,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 5
        },
        "тыква": {
            "name_ru": "Тыква",
            "name_en": "Pumpkin",
            "name_uz": "Qovoq",
            "calories_per_100g": 26,
            "protein_per_100g": 1.0,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 6.5,
            "category": "vegetables",
            "cooking_methods": ["bake", "boil", "steam"],
            "cooking_time_minutes": 20,
            "price_tier": "low",
            "availability": "high",
            "shelf_life_days": 60
        },

        # БОЛЬШЕ ФРУКТОВ
        "киви": {
            "name_ru": "Киви",
            "name_en": "Kiwi",
            "name_uz": "Kivi",
            "calories_per_100g": 61,
            "protein_per_100g": 1.1,
            "fat_per_100g": 0.5,
            "carbs_per_100g": 15.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 7
        },
        "манго": {
            "name_ru": "Манго",
            "name_en": "Mango",
            "name_uz": "Mango",
            "calories_per_100g": 60,
            "protein_per_100g": 0.8,
            "fat_per_100g": 0.4,
            "carbs_per_100g": 15.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 5
        },
        "грейпфрут": {
            "name_ru": "Грейпфрут",
            "name_en": "Grapefruit",
            "name_uz": "Greypfrut",
            "calories_per_100g": 42,
            "protein_per_100g": 0.8,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 11.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 14
        },
        "ананас": {
            "name_ru": "Ананас",
            "name_en": "Pineapple",
            "name_uz": "Ananas",
            "calories_per_100g": 50,
            "protein_per_100g": 0.5,
            "fat_per_100g": 0.1,
            "carbs_per_100g": 13.0,
            "category": "fruits",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 5
        },

        # ДОПОЛНИТЕЛЬНЫЕ ЖИРЫ
        "семена_чиа": {
            "name_ru": "Семена чиа",
            "name_en": "Chia seeds",
            "name_uz": "Chia urug'i",
            "calories_per_100g": 486,
            "protein_per_100g": 17.0,
            "fat_per_100g": 31.0,
            "carbs_per_100g": 42.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "medium",
            "shelf_life_days": 365
        },
        "семена_льна": {
            "name_ru": "Семена льна",
            "name_en": "Flax seeds",
            "name_uz": "Zig'ir urug'i",
            "calories_per_100g": 534,
            "protein_per_100g": 18.0,
            "fat_per_100g": 42.0,
            "carbs_per_100g": 29.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 365
        },
        "кешью": {
            "name_ru": "Кешью",
            "name_en": "Cashews",
            "name_uz": "Keshyu",
            "calories_per_100g": 553,
            "protein_per_100g": 18.0,
            "fat_per_100g": 44.0,
            "carbs_per_100g": 30.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 180
        },
        "фундук": {
            "name_ru": "Фундук",
            "name_en": "Hazelnuts",
            "name_uz": "Funduk",
            "calories_per_100g": 628,
            "protein_per_100g": 15.0,
            "fat_per_100g": 61.0,
            "carbs_per_100g": 17.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "high",
            "availability": "high",
            "shelf_life_days": 180
        },
        "арахисовая_паста": {
            "name_ru": "Арахисовая паста",
            "name_en": "Peanut butter",
            "name_uz": "Yeryong'oq pastasi",
            "calories_per_100g": 588,
            "protein_per_100g": 25.0,
            "fat_per_100g": 50.0,
            "carbs_per_100g": 20.0,
            "category": "nuts",
            "cooking_methods": ["raw"],
            "cooking_time_minutes": 0,
            "price_tier": "medium",
            "availability": "high",
            "shelf_life_days": 180
        },
    }

    @classmethod
    def get_product(cls, product_key: str) -> Optional[dict]:
        """Получить информацию о продукте"""
        return cls.PRODUCTS.get(product_key)

    @classmethod
    def get_product_by_name(cls, name: str, language: str = "ru") -> Optional[dict]:
        """Найти продукт по названию"""
        name_key = f"name_{language}"
        for key, product in cls.PRODUCTS.items():
            if product.get(name_key, "").lower() == name.lower():
                result = product.copy()
                result['key'] = key
                return result
        return None

    @classmethod
    def search_by_category(cls, category: str) -> List[dict]:
        """Найти все продукты категории"""
        results = []
        for key, product in cls.PRODUCTS.items():
            if product["category"] == category:
                p = product.copy()
                p['key'] = key
                results.append(p)
        return results

    @classmethod
    def calculate_nutrition(cls, product_key: str, grams: int) -> dict:
        """Рассчитать питательность порции"""
        product = cls.get_product(product_key)
        if not product:
            return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

        ratio = grams / 100.0

        return {
            "calories": round(product["calories_per_100g"] * ratio),
            "protein": round(product["protein_per_100g"] * ratio, 1),
            "fat": round(product["fat_per_100g"] * ratio, 1),
            "carbs": round(product["carbs_per_100g"] * ratio, 1)
        }

    @classmethod
    def get_all_products(cls) -> List[dict]:
        """Получить все продукты с ключами"""
        results = []
        for key, product in cls.PRODUCTS.items():
            p = product.copy()
            p['key'] = key
            results.append(p)
        return results


class RecipeDatabase:
    """База готовых рецептов"""

    # Используем recipes_loader для загрузки рецептов из book/
    # Инициализация происходит через _init_recipes()
    RECIPES = {}

    # Старая версия с 5 рецептами (закомментирована):
    """
    OLD_RECIPES = {
        "овсянка_с_фруктами": {
            "name_ru": "Овсянка с фруктами и орехами",
            "name_en": "Oatmeal with fruits and nuts",
            "name_uz": "Mevali jo'xori",
            "meal_type": "breakfast",
            "difficulty": "easy",
            "cooking_time_minutes": 10,
            "ingredients": {
                "овсянка": 50,
                "молоко": 200,
                "яблоко": 100,
                "грецкие_орехи": 15,
                "мед": 10
            },
            "steps_ru": [
                "Вскипятите молоко в маленькой кастрюле",
                "Добавьте овсяные хлопья и варите 5 минут, помешивая",
                "Нарежьте яблоко небольшими кусочками",
                "Измельчите грецкие орехи",
                "Разложите кашу по тарелке",
                "Добавьте яблоко, орехи и полейте медом"
            ],
            "steps_en": [
                "Boil milk in a small pot",
                "Add oats and cook for 5 minutes, stirring",
                "Cut apple into small pieces",
                "Chop walnuts",
                "Place porridge on a plate",
                "Add apple, nuts and drizzle with honey"
            ],
            "steps_uz": [
                "Sutni qozonda qaynatib oling",
                "Jo'xorini qo'shing va 5 daqiqa pishiring",
                "Olmani mayda bo'laklarga to'g'rang",
                "Yong'oqni maydalang",
                "Likopchalarga solib bering",
                "Olma, yong'oq qo'shing va asal qo'shing"
            ],
            "tips_ru": "Овсянка содержит клетчатку, которая помогает чувствовать сытость дольше и улучшает пищеварение.",
            "tips_en": "Oatmeal contains fiber that helps you feel full longer and improves digestion.",
            "tips_uz": "Jo'xori tola ichadi, bu uzoq vaqt to'yinganlik hissi beradi va hazm qilishni yaxshilaydi."
        },
        "яичница_с_овощами": {
            "name_ru": "Яичница с овощами",
            "name_en": "Scrambled eggs with vegetables",
            "name_uz": "Sabzavotli tuxum",
            "meal_type": "breakfast",
            "difficulty": "easy",
            "cooking_time_minutes": 10,
            "ingredients": {
                "яйца": 150,  # 3 яйца
                "помидоры": 100,
                "болгарский_перец": 80,
                "шпинат": 50,
                "оливковое_масло": 5
            },
            "steps_ru": [
                "Нарежьте помидоры и перец небольшими кубиками",
                "Разогрейте сковороду с оливковым маслом",
                "Обжарьте овощи 3-4 минуты",
                "Добавьте шпинат и готовьте 1 минуту",
                "Взбейте яйца и влейте в сковороду",
                "Помешивая, готовьте до желаемой консистенции"
            ],
            "steps_en": [
                "Dice tomatoes and bell pepper into small cubes",
                "Heat pan with olive oil",
                "Sauté vegetables for 3-4 minutes",
                "Add spinach and cook for 1 minute",
                "Beat eggs and pour into pan",
                "Cook while stirring to desired consistency"
            ],
            "steps_uz": [
                "Pomidor va qalampirni kichik kubiklarga to'g'rang",
                "Zaytun moyi bilan idishni qizdiring",
                "Sabzavotlarni 3-4 daqiqa qovuring",
                "Ismaloq qo'shing va 1 daqiqa pishiring",
                "Tuxumni ko'pirtiring va idishga quying",
                "Aralashtirib, kerakli holatgacha pishiring"
            ],
            "tips_ru": "Яйца — отличный источник белка и витаминов. Овощи добавляют клетчатку и антиоксиданты.",
            "tips_en": "Eggs are an excellent source of protein and vitamins. Vegetables add fiber and antioxidants.",
            "tips_uz": "Tuxum protein va vitaminlar manbai. Sabzavotlar tola va antioksidantlar beradi."
        },
        "курица_с_рисом": {
            "name_ru": "Куриная грудка с рисом и овощами",
            "name_en": "Chicken breast with rice and vegetables",
            "name_uz": "Tovuq ko'kragi guruch va sabzavotlar bilan",
            "meal_type": "lunch",
            "difficulty": "medium",
            "cooking_time_minutes": 40,
            "ingredients": {
                "куриная_грудка": 150,
                "рис_белый": 80,  # сухой вес
                "брокколи": 150,
                "морковь": 80,
                "оливковое_масло": 10
            },
            "steps_ru": [
                "Промойте рис и отварите в подсоленной воде 20 минут",
                "Нарежьте куриную грудку на средние кусочки",
                "Разогрейте сковороду с маслом и обжарьте курицу 10-12 минут",
                "Нарежьте брокколи и морковь",
                "Приготовьте овощи на пару или отварите 5-7 минут",
                "Подавайте курицу с рисом и овощами"
            ],
            "steps_en": [
                "Rinse rice and boil in salted water for 20 minutes",
                "Cut chicken breast into medium pieces",
                "Heat pan with oil and cook chicken for 10-12 minutes",
                "Cut broccoli and carrots",
                "Steam or boil vegetables for 5-7 minutes",
                "Serve chicken with rice and vegetables"
            ],
            "steps_uz": [
                "Guruchni yuving va tuzli suvda 20 daqiqa qaynatib oling",
                "Tovuq ko'kragini o'rtacha bo'laklarga to'g'rang",
                "Idishni moy bilan qizdiring va tovuqni 10-12 daqiqa pishiring",
                "Brokkoli va sabzini to'g'rang",
                "Sabzavotlarni bug'da yoki qaynatib 5-7 daqiqa pishiring",
                "Tovuqni guruch va sabzavotlar bilan bering"
            ],
            "tips_ru": "Куриная грудка — это нежирный источник белка, идеально подходящий для набора мышечной массы.",
            "tips_en": "Chicken breast is a lean protein source, perfect for building muscle mass.",
            "tips_uz": "Tovuq ko'kragi yog'siz protein manbai, mushak massasini oshirish uchun juda yaxshi."
        },
        "рыба_с_овощами": {
            "name_ru": "Запечённая рыба с овощами",
            "name_en": "Baked fish with vegetables",
            "name_uz": "Pishirilgan baliq sabzavotlar bilan",
            "meal_type": "dinner",
            "difficulty": "medium",
            "cooking_time_minutes": 30,
            "ingredients": {
                "рыба_треска": 180,
                "брокколи": 100,
                "кабачок": 100,
                "помидоры": 80,
                "оливковое_масло": 10
            },
            "steps_ru": [
                "Разогрейте духовку до 200°C",
                "Нарежьте овощи крупными кусками",
                "Выложите рыбу и овощи на противень",
                "Сбрызните оливковым маслом, посолите",
                "Запекайте 20-25 минут до готовности",
                "Подавайте горячим"
            ],
            "steps_en": [
                "Preheat oven to 200°C (400°F)",
                "Cut vegetables into large chunks",
                "Place fish and vegetables on baking sheet",
                "Drizzle with olive oil and salt",
                "Bake for 20-25 minutes until done",
                "Serve hot"
            ],
            "steps_uz": [
                "Pechni 200°C ga qizdiring",
                "Sabzavotlarni katta bo'laklarga to'g'rang",
                "Baliq va sabzavotlarni pechga qo'ying",
                "Zaytun moyi va tuz seping",
                "20-25 daqiqa pishiring",
                "Issiq holda bering"
            ],
            "tips_ru": "Треска — низкокалорийная рыба с высоким содержанием белка. Идеальна для ужина.",
            "tips_en": "Cod is a low-calorie fish high in protein. Perfect for dinner.",
            "tips_uz": "Treska kam kaloriyali, protein bilan boy baliq. Kechki ovqat uchun ideal."
        },
        "творог_с_ягодами": {
            "name_ru": "Творог с ягодами и медом",
            "name_en": "Cottage cheese with berries and honey",
            "name_uz": "Tvorog mevalar va asal bilan",
            "meal_type": "snack",
            "difficulty": "easy",
            "cooking_time_minutes": 5,
            "ingredients": {
                "творог": 200,
                "ягоды": 100,
                "мед": 15,
                "грецкие_орехи": 10
            },
            "steps_ru": [
                "Выложите творог в миску",
                "Добавьте ягоды",
                "Полейте медом",
                "Посыпьте измельченными орехами",
                "Перемешайте и подавайте"
            ],
            "steps_en": [
                "Place cottage cheese in a bowl",
                "Add berries",
                "Drizzle with honey",
                "Sprinkle with chopped nuts",
                "Mix and serve"
            ],
            "steps_uz": [
                "Tvorogni idishga soling",
                "Mevalarni qo'shing",
                "Asal qo'shing",
                "Maydalangan yong'oq seping",
                "Aralashtirib bering"
            ],
            "tips_ru": "Творог богат казеиновым белком, который медленно усваивается и надолго насыщает.",
            "tips_en": "Cottage cheese is rich in casein protein, which digests slowly and provides long-lasting satiety.",
            "tips_uz": "Tvorog kazein proteini bilan boy, sekin hazm bo'ladi va uzoq vaqt to'yintiradi."
        }
    }
    """

    @classmethod
    def get_recipe(cls, recipe_key: str) -> Optional[dict]:
        """Получить рецепт по ключу"""
        # Используем recipes_loader для получения рецепта
        return recipes_loader.get_recipe("", recipe_key)

    @classmethod
    def search_by_meal_type(cls, meal_type: str, goal: str = 'maintain') -> List[dict]:
        """Найти все рецепты для типа приёма пищи с учетом цели"""
        # Маппинг типов еды
        meal_map = {
            'breakfast': 'завтрак',
            'lunch': 'обед',
            'dinner': 'ужин',
            'snack': 'завтрак',  # snacks используют завтраки
            'snack1': 'завтрак',
            'snack2': 'завтрак'
        }

        # Получаем рецепты через recipes_loader с учетом цели
        meal_type_ru = meal_map.get(meal_type, meal_type)
        recipes = recipes_loader.get_recipes(goal, meal_type_ru, count=20)

        # Добавляем meal_type к каждому рецепту для совместимости
        for recipe in recipes:
            if 'meal_type' not in recipe:
                recipe['meal_type'] = meal_type

        return recipes


class ExerciseDatabase:
    """База упражнений"""

    EXERCISES = {
        # ГРУДЬ
        "отжимания": {
            "name_ru": "Отжимания от пола",
            "name_en": "Push-ups",
            "name_uz": "Poldan turib",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.5,
            "technique_ru": "Руки на ширине плеч, тело прямое от головы до пяток. Опускайтесь до касания грудью пола, затем выжимайте себя вверх.",
            "technique_en": "Hands shoulder-width apart, body straight from head to heels. Lower until chest touches floor, then push yourself up.",
            "technique_uz": "Qo'llar yelka kengligida, tana boshdan to tovongacha to'g'ri. Ko'krak polga tegguncha pastga tushing, keyin yuqoriga ko'taring.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Неполная амплитуда", "Неправильное положение рук", "Задержка дыхания"],
            "common_mistakes_en": ["Lower back sag", "Partial range of motion", "Incorrect hand position", "Holding breath"],
            "common_mistakes_uz": ["Bel egilishi", "To'liq harakat yo'q", "Qo'llar noto'g'ri joylashgan", "Nafasni ushlab turish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 45}
            }
        },
        "жим_лежа": {
            "name_ru": "Жим штанги лёжа",
            "name_en": "Barbell bench press",
            "name_uz": "Yotgan holatda shtanga ko'tarish",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "barbell",
            "difficulty": "intermediate",
            "calories_per_rep": 1.2,
            "technique_ru": "Лягте на скамью, стопы на полу. Возьмите штангу шире плеч. Опустите к груди, затем выжмите вверх.",
            "technique_en": "Lie on bench, feet on floor. Grip barbell wider than shoulders. Lower to chest, then press up.",
            "technique_uz": "Skameykada yoting, oyoqlar polda. Shtangani yelkalardan kengroq ushlang. Ko'krakka tushiring, keyin yuqoriga ko'taring.",
            "common_mistakes_ru": ["Отрыв ягодиц от скамьи", "Слишком быстрое опускание", "Неправильный хват"],
            "common_mistakes_en": ["Lifting buttocks off bench", "Lowering too fast", "Incorrect grip"],
            "common_mistakes_uz": ["Skameykadan ko'tarilish", "Juda tez tushirish", "Noto'g'ri ushlash"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-10", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "6-10", "rest_seconds": 90}
            }
        },

        # СПИНА
        "подтягивания": {
            "name_ru": "Подтягивания",
            "name_en": "Pull-ups",
            "name_uz": "Turnikda tortish",
            "muscle_groups": ["back", "biceps"],
            "equipment": "pull_up_bar",
            "difficulty": "intermediate",
            "calories_per_rep": 1.0,
            "technique_ru": "Повисните на турнике хватом шире плеч. Подтяните себя вверх до подбородка над перекладиной.",
            "technique_en": "Hang from bar with grip wider than shoulders. Pull yourself up until chin is over the bar.",
            "technique_uz": "Turnikda osilib, yelkadan keng ushlang. Iyagingiz turnikdan yuqoriga chiqguncha tortib ko'taring.",
            "common_mistakes_ru": ["Раскачивание тела", "Неполная амплитуда", "Слишком узкий хват"],
            "common_mistakes_en": ["Body swinging", "Partial range of motion", "Grip too narrow"],
            "common_mistakes_uz": ["Tanani tebratish", "To'liq harakat yo'q", "Ushlash juda tor"],
            "progression": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "12-15", "rest_seconds": 60}
            }
        },
        "тяга_штанги": {
            "name_ru": "Тяга штанги в наклоне",
            "name_en": "Barbell row",
            "name_uz": "Egilib shtanga tortish",
            "muscle_groups": ["back", "biceps"],
            "equipment": "barbell",
            "difficulty": "intermediate",
            "calories_per_rep": 1.1,
            "technique_ru": "Наклонитесь вперёд, спина прямая. Тяните штангу к нижней части живота, сводя лопатки.",
            "technique_en": "Bend forward, back straight. Pull barbell to lower abdomen, squeezing shoulder blades.",
            "technique_uz": "Oldinga egiling, orqa to'g'ri. Shtangani qorin pastiga torting, yelka suyaklarini birlashtiring.",
            "common_mistakes_ru": ["Округление спины", "Слишком высокий подъём", "Рывки"],
            "common_mistakes_en": ["Rounding back", "Lifting too high", "Jerking movements"],
            "common_mistakes_uz": ["Orqani egish", "Juda baland ko'tarish", "Silkinish harakatlari"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-12", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "10-12", "rest_seconds": 60}
            }
        },

        # НОГИ
        "приседания": {
            "name_ru": "Приседания",
            "name_en": "Squats",
            "name_uz": "Cho'kkalab turib",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.8,
            "technique_ru": "Ноги на ширине плеч, спина прямая. Опускайтесь, отводя таз назад, до параллели бёдер с полом.",
            "technique_en": "Feet shoulder-width apart, back straight. Lower down, pushing hips back, until thighs parallel to floor.",
            "technique_uz": "Oyoqlar yelka kengligida, orqa to'g'ri. Kesib pastga tushing, sonni orqaga surting, son pollga parallel bo'lguncha.",
            "common_mistakes_ru": ["Колени выходят за носки", "Округление спины", "Недостаточная глубина"],
            "common_mistakes_en": ["Knees go past toes", "Rounding back", "Insufficient depth"],
            "common_mistakes_uz": ["Tizzalar oyoq barmoqlaridan o'tadi", "Orqani egish", "Yetarli chuqurlik yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "20-25", "rest_seconds": 45}
            }
        },
        "выпады": {
            "name_ru": "Выпады",
            "name_en": "Lunges",
            "name_uz": "Oldinga qadam",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.6,
            "technique_ru": "Сделайте шаг вперёд, опуститесь вниз, сгибая оба колена под 90°. Вернитесь в исходное положение.",
            "technique_en": "Step forward, lower down by bending both knees to 90°. Return to starting position.",
            "technique_uz": "Oldinga qadam qo'ying, ikkala tizzani 90° ga bukib pastga tushing. Boshlang'ich holatga qayting.",
            "common_mistakes_ru": ["Колено передней ноги выходит за носок", "Наклон корпуса", "Короткий шаг"],
            "common_mistakes_en": ["Front knee goes past toe", "Leaning torso", "Short step"],
            "common_mistakes_uz": ["Old oyoq tizzasi barmoqdan o'tadi", "Tanani egish", "Qisqa qadam"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-12 на ногу", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-15 на ногу", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "15-20 на ногу", "rest_seconds": 45}
            }
        },
        "становая_тяга": {
            "name_ru": "Становая тяга",
            "name_en": "Deadlift",
            "name_uz": "To'liq tortish",
            "muscle_groups": ["back", "legs", "glutes"],
            "equipment": "barbell",
            "difficulty": "advanced",
            "calories_per_rep": 1.5,
            "technique_ru": "Ноги на ширине бёдер, штанга над стопами. Наклонитесь, возьмите штангу. Выпрямитесь, поднимая штангу вдоль ног.",
            "technique_en": "Feet hip-width apart, bar over feet. Bend down, grip bar. Straighten up, lifting bar along legs.",
            "technique_uz": "Oyoqlar son kengligida, shtanga oyoqlar ustida. Egilib, shtangani ushlang. To'g'rilanib, shtangani oyoqlar bo'ylab ko'taring.",
            "common_mistakes_ru": ["Округление спины", "Отрыв штанги от ног", "Разгибание только спины"],
            "common_mistakes_en": ["Rounding back", "Bar away from legs", "Using only back to lift"],
            "common_mistakes_uz": ["Orqani egish", "Shtangani oyoqlardan uzoqlashtirish", "Faqat orqa bilan ko'tarish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-8", "rest_seconds": 150},
                "intermediate": {"sets": 4, "reps": "6-10", "rest_seconds": 120},
                "advanced": {"sets": 5, "reps": "5-8", "rest_seconds": 120}
            }
        },
        "жим_ногами": {
            "name_ru": "Жим ногами в тренажёре",
            "name_en": "Leg press",
            "name_uz": "Trenajyorda oyoq pressi",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "machine",
            "difficulty": "beginner",
            "calories_per_rep": 1.0,
            "technique_ru": "Сядьте в тренажёр, стопы на платформе на ширине плеч. Опустите платформу, сгибая колени до 90°, затем выжмите вверх.",
            "technique_en": "Sit in machine, feet on platform shoulder-width apart. Lower platform by bending knees to 90°, then press up.",
            "technique_uz": "Trenajyorga o'tiring, oyoqlar platformada yelka kengligida. Tizzalarni 90° ga bukib platformani tushiring, keyin yuqoriga siqing.",
            "common_mistakes_ru": ["Отрыв поясницы от спинки", "Колени внутрь", "Неполная амплитуда"],
            "common_mistakes_en": ["Lower back leaving seat", "Knees caving in", "Partial range of motion"],
            "common_mistakes_uz": ["Belni o'rindiqdan ko'tarish", "Tizzalar ichkariga", "To'liq harakat yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-12", "rest_seconds": 90},
                "advanced": {"sets": 4, "reps": "8-10", "rest_seconds": 90}
            }
        },
        "сгибания_ног": {
            "name_ru": "Сгибания ног в тренажёре",
            "name_en": "Lying leg curls",
            "name_uz": "Trenajyorda oyoq bukish",
            "muscle_groups": ["legs", "hamstrings"],
            "equipment": "machine",
            "difficulty": "beginner",
            "calories_per_rep": 0.6,
            "technique_ru": "Лягте на тренажёр лицом вниз, валик над пятками. Сгибайте ноги, подтягивая валик к ягодицам.",
            "technique_en": "Lie face down on machine, pad above ankles. Curl legs up, bringing pad toward glutes.",
            "technique_uz": "Trenajyorga yuz bilan yoting, valik to'piqlar ustida. Oyoqlarni bukib, valikni dumbaga torting.",
            "common_mistakes_ru": ["Отрыв бёдер от скамьи", "Рывки", "Слишком быстрое опускание"],
            "common_mistakes_en": ["Hips lifting off bench", "Jerking movements", "Lowering too fast"],
            "common_mistakes_uz": ["Sonlarni skameykadan ko'tarish", "Silkitish", "Juda tez tushirish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "10-12", "rest_seconds": 45}
            }
        },
        "разгибания_ног": {
            "name_ru": "Разгибания ног в тренажёре",
            "name_en": "Leg extensions",
            "name_uz": "Trenajyorda oyoq yozish",
            "muscle_groups": ["legs", "quadriceps"],
            "equipment": "machine",
            "difficulty": "beginner",
            "calories_per_rep": 0.5,
            "technique_ru": "Сядьте на тренажёр, валик над голеностопом. Разгибайте ноги до полного выпрямления.",
            "technique_en": "Sit on machine, pad above ankles. Extend legs to full straightening.",
            "technique_uz": "Trenajyorga o'tiring, valik to'piqlar ustida. Oyoqlarni to'liq to'g'rilanguncha yozing.",
            "common_mistakes_ru": ["Отрыв спины от спинки", "Рывки", "Неполная амплитуда"],
            "common_mistakes_en": ["Back leaving seat", "Jerking", "Partial range of motion"],
            "common_mistakes_uz": ["Orqani o'rindiqdan ko'tarish", "Silkitish", "To'liq harakat yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "10-12", "rest_seconds": 45}
            }
        },
        "подъем_на_носки": {
            "name_ru": "Подъём на носки стоя",
            "name_en": "Standing calf raises",
            "name_uz": "Turgan holatda tovonlarni ko'tarish",
            "muscle_groups": ["legs", "calves"],
            "equipment": "machine",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Встаньте на платформу носками, пятки свисают. Поднимитесь на носки максимально вверх, затем опуститесь.",
            "technique_en": "Stand on platform on toes, heels hanging off. Rise up on toes as high as possible, then lower.",
            "technique_uz": "Platformada oyoq barmoqlarida turing, tovonlar osilib turadi. Iloji boricha yuqoriga ko'taring, keyin tushiring.",
            "common_mistakes_ru": ["Сгибание коленей", "Неполная амплитуда", "Слишком быстрый темп"],
            "common_mistakes_en": ["Bending knees", "Partial range of motion", "Too fast tempo"],
            "common_mistakes_uz": ["Tizzalarni bukish", "To'liq harakat yo'q", "Juda tez temp"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 45},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "румынская_тяга": {
            "name_ru": "Румынская тяга",
            "name_en": "Romanian deadlift",
            "name_uz": "Ruminiya tortish",
            "muscle_groups": ["legs", "glutes", "hamstrings"],
            "equipment": "barbell",
            "difficulty": "intermediate",
            "calories_per_rep": 1.2,
            "technique_ru": "Встаньте со штангой, ноги на ширине бёдер. Наклоняйтесь вперёд с прямой спиной, отводя таз назад, штанга скользит по ногам.",
            "technique_en": "Stand with barbell, feet hip-width. Hinge forward with straight back, pushing hips back, bar slides along legs.",
            "technique_uz": "Shtanga bilan turing, oyoqlar son kengligida. To'g'ri orqa bilan oldinga egiling, kesib orqaga suring, shtanga oyoqlar bo'ylab sirg'anadi.",
            "common_mistakes_ru": ["Округление спины", "Сгибание коленей", "Штанга далеко от ног"],
            "common_mistakes_en": ["Rounding back", "Bending knees too much", "Bar away from legs"],
            "common_mistakes_uz": ["Orqani egish", "Tizzalarni ko'p bukish", "Shtanga oyoqlardan uzoq"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-12", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "8-10", "rest_seconds": 60}
            }
        },
        "болгарские_выпады": {
            "name_ru": "Болгарские выпады",
            "name_en": "Bulgarian split squats",
            "name_uz": "Bolgar bo'lingan cho'kish",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "dumbbells",
            "difficulty": "intermediate",
            "calories_per_rep": 0.8,
            "technique_ru": "Задняя нога на скамье, передняя на полу. Опускайтесь вниз, сгибая переднюю ногу до 90°.",
            "technique_en": "Rear foot on bench, front foot on floor. Lower down by bending front leg to 90°.",
            "technique_uz": "Orqa oyoq skameykada, old oyoq polda. Old oyoqni 90° ga bukib pastga tushing.",
            "common_mistakes_ru": ["Колено за носком", "Наклон корпуса", "Потеря баланса"],
            "common_mistakes_en": ["Knee past toes", "Leaning torso", "Losing balance"],
            "common_mistakes_uz": ["Tizza barmoqdan o'tadi", "Tanani egish", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-10 на ногу", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-12 на ногу", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "12-15 на ногу", "rest_seconds": 60}
            }
        },

        # ПЛЕЧИ
        "жим_гантелей_стоя": {
            "name_ru": "Жим гантелей стоя",
            "name_en": "Dumbbell shoulder press",
            "name_uz": "Tik turgan holatda gantel ko'tarish",
            "muscle_groups": ["shoulders", "triceps"],
            "equipment": "dumbbells",
            "difficulty": "intermediate",
            "calories_per_rep": 0.9,
            "technique_ru": "Встаньте прямо, гантели на уровне плеч. Выжмите их вверх над головой, затем опустите.",
            "technique_en": "Stand straight, dumbbells at shoulder level. Press them overhead, then lower.",
            "technique_uz": "To'g'ri turing, gantellar yelka darajasida. Ularni bosh ustida ko'taring, keyin tushiring.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Толчок ногами", "Неполная амплитуда"],
            "common_mistakes_en": ["Arching lower back", "Using leg drive", "Partial range of motion"],
            "common_mistakes_uz": ["Belni egish", "Oyoq bilan itarish", "To'liq harakat yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-12", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "12-15", "rest_seconds": 60}
            }
        },

        # РУКИ
        "подъем_штанги_на_бицепс": {
            "name_ru": "Подъём штанги на бицепс",
            "name_en": "Barbell bicep curl",
            "name_uz": "Shtanga bilan bitseps mashqi",
            "muscle_groups": ["biceps"],
            "equipment": "barbell",
            "difficulty": "beginner",
            "calories_per_rep": 0.4,
            "technique_ru": "Встаньте прямо, штанга в опущенных руках. Сгибайте руки, поднимая штангу к плечам.",
            "technique_en": "Stand straight, barbell in lowered hands. Curl arms, lifting barbell to shoulders.",
            "technique_uz": "To'g'ri turing, shtanga tushirilgan qo'llarda. Qo'llarni bukib, shtangani yelkalarga ko'taring.",
            "common_mistakes_ru": ["Раскачивание корпуса", "Отведение локтей", "Слишком быстрое опускание"],
            "common_mistakes_en": ["Swinging torso", "Moving elbows", "Lowering too fast"],
            "common_mistakes_uz": ["Tanani tebratish", "Tirsak harakatlanishi", "Juda tez tushirish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-12", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "12-15", "rest_seconds": 45}
            }
        },
        "французский_жим": {
            "name_ru": "Французский жим лёжа",
            "name_en": "Lying tricep extension",
            "name_uz": "Yotgan holatda tritseps mashqi",
            "muscle_groups": ["triceps"],
            "equipment": "barbell",
            "difficulty": "intermediate",
            "calories_per_rep": 0.5,
            "technique_ru": "Лягте на скамью, штанга над головой. Сгибайте руки в локтях, опуская штангу ко лбу.",
            "technique_en": "Lie on bench, barbell overhead. Bend at elbows, lowering barbell to forehead.",
            "technique_uz": "Skameykada yoting, shtanga bosh ustida. Tirsаklarni bukib, shtangani peshonaga tushiring.",
            "common_mistakes_ru": ["Разведение локтей", "Движение плечами", "Слишком тяжёлый вес"],
            "common_mistakes_en": ["Flaring elbows", "Moving shoulders", "Weight too heavy"],
            "common_mistakes_uz": ["Tirsaklarni kengaytirish", "Yelkalarni harakatlantirish", "Juda og'ir vazn"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-12", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "12-15", "rest_seconds": 45}
            }
        },

        # ПРЕСС
        "скручивания": {
            "name_ru": "Скручивания",
            "name_en": "Crunches",
            "name_uz": "Press mashqi",
            "muscle_groups": ["abs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Лягте на спину, ноги согнуты. Поднимайте плечи от пола, напрягая пресс.",
            "technique_en": "Lie on back, knees bent. Lift shoulders off floor, contracting abs.",
            "technique_uz": "Orqaga yoting, tizzalar bukilgan. Yelkalarni poldan ko'taring, pressni tarang qiling.",
            "common_mistakes_ru": ["Рывки головой", "Отрыв поясницы", "Слишком высокий подъём"],
            "common_mistakes_en": ["Jerking head", "Lifting lower back", "Rising too high"],
            "common_mistakes_uz": ["Boshni silkitish", "Belni ko'tarish", "Juda baland ko'tarilish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 45},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },
        "планка": {
            "name_ru": "Планка",
            "name_en": "Plank",
            "name_uz": "Planka",
            "muscle_groups": ["abs", "core"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_second": 0.05,
            "technique_ru": "Упритесь на предплечья и носки, тело прямое. Держите позицию, напрягая пресс.",
            "technique_en": "Support on forearms and toes, body straight. Hold position, contracting abs.",
            "technique_uz": "Bilaklaringiz va barmoqlaringizga suyaning, tana to'g'ri. Holatni saqlang, pressni tarang qiling.",
            "common_mistakes_ru": ["Провисание бёдер", "Подъём ягодиц", "Задержка дыхания"],
            "common_mistakes_en": ["Sagging hips", "Raising buttocks", "Holding breath"],
            "common_mistakes_uz": ["Keskin tushib ketish", "Ko'tarilish", "Nafasni ushlab turish"],
            "progression": {
                "beginner": {"sets": 3, "duration_seconds": 30, "rest_seconds": 60},
                "intermediate": {"sets": 3, "duration_seconds": 60, "rest_seconds": 60},
                "advanced": {"sets": 4, "duration_seconds": 90, "rest_seconds": 45}
            }
        },

        # КАРДИО
        "бег": {
            "name_ru": "Бег",
            "name_en": "Running",
            "name_uz": "Yugurish",
            "muscle_groups": ["cardio", "legs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_minute": 10,
            "technique_ru": "Естественный шаг, руки согнуты в локтях. Приземляйтесь на середину стопы.",
            "technique_en": "Natural stride, arms bent at elbows. Land on midfoot.",
            "technique_uz": "Tabiiy qadam, qo'llar tirsak bukib. Oyoq o'rtasiga tushing.",
            "common_mistakes_ru": ["Удар пяткой", "Слишком длинный шаг", "Напряжение плеч"],
            "common_mistakes_en": ["Heel striking", "Overstriding", "Tense shoulders"],
            "common_mistakes_uz": ["Tovon bilan urilish", "Juda uzun qadam", "Yelka tarangligi"],
            "progression": {
                "beginner": {"duration_minutes": 20, "intensity": "light"},
                "intermediate": {"duration_minutes": 30, "intensity": "moderate"},
                "advanced": {"duration_minutes": 45, "intensity": "high"}
            }
        },
        "прыжки_на_скакалке": {
            "name_ru": "Прыжки на скакалке",
            "name_en": "Jump rope",
            "name_uz": "Arqon bilan sakrash",
            "muscle_groups": ["cardio", "legs", "shoulders"],
            "equipment": "jump_rope",
            "difficulty": "beginner",
            "calories_per_minute": 12,
            "technique_ru": "Лёгкие прыжки на носках, вращение скакалки запястьями.",
            "technique_en": "Light bounces on toes, rotate rope with wrists.",
            "technique_uz": "Barmoqlarda yengil sakrashlar, arqonni bilaklaringiz bilan aylantiring.",
            "common_mistakes_ru": ["Высокие прыжки", "Вращение руками", "Прыжки на всей стопе"],
            "common_mistakes_en": ["Jumping too high", "Rotating with arms", "Landing on whole foot"],
            "common_mistakes_uz": ["Juda baland sakrash", "Qo'llar bilan aylantirish", "Butun oyoqqa tushish"],
            "progression": {
                "beginner": {"duration_minutes": 5, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_minutes": 10, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_minutes": 15, "sets": 3, "rest_seconds": 30}
            }
        },
        "велотренажер": {
            "name_ru": "Велотренажёр",
            "name_en": "Stationary bike",
            "name_uz": "Velotrenazhyor",
            "muscle_groups": ["cardio", "legs"],
            "equipment": "bike",
            "difficulty": "beginner",
            "calories_per_minute": 8,
            "technique_ru": "Умеренный темп, сопротивление по ощущениям. Спина прямая.",
            "technique_en": "Moderate pace, resistance as comfortable. Back straight.",
            "technique_uz": "O'rtacha tezlik, qarshilikni o'zingizga qulay qilib sozlang. Orqa to'g'ri.",
            "common_mistakes_ru": ["Слишком низкое сидение", "Сутулость", "Блокировка коленей"],
            "common_mistakes_en": ["Seat too low", "Slouching", "Locking knees"],
            "common_mistakes_uz": ["O'rindiq juda past", "Eglib o'tirish", "Tizzalarni qotirish"],
            "progression": {
                "beginner": {"duration_minutes": 15, "intensity": "light"},
                "intermediate": {"duration_minutes": 25, "intensity": "moderate"},
                "advanced": {"duration_minutes": 40, "intensity": "high"}
            }
        },

        # ============ УПРАЖНЕНИЯ С ТУРНИКОМ ============
        "подтягивания_узким_хватом": {
            "name_ru": "Подтягивания узким хватом",
            "name_en": "Close grip pull-ups",
            "name_uz": "Tor ushlash bilan turnikda tortish",
            "muscle_groups": ["back", "biceps"],
            "equipment": "pull_up_bar",
            "difficulty": "intermediate",
            "calories_per_rep": 1.1,
            "technique_ru": "Хват уже ширины плеч, ладони к себе. Подтягивайтесь до подбородка.",
            "technique_en": "Grip narrower than shoulder width, palms facing you. Pull up to chin level.",
            "technique_uz": "Yelkadan torroq ushlash, kaftlar o'zingizga qarab. Iyagingiz darajasiga torting.",
            "common_mistakes_ru": ["Раскачивание", "Неполная амплитуда", "Слишком быстрый темп"],
            "common_mistakes_en": ["Swinging", "Partial ROM", "Too fast tempo"],
            "common_mistakes_uz": ["Tebranish", "To'liq harakat yo'q", "Juda tez"],
            "progression": {
                "beginner": {"sets": 3, "reps": "4-6", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "6-10", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "10-15", "rest_seconds": 60}
            }
        },
        "подтягивания_широким_хватом": {
            "name_ru": "Подтягивания широким хватом",
            "name_en": "Wide grip pull-ups",
            "name_uz": "Keng ushlash bilan turnikda tortish",
            "muscle_groups": ["back", "shoulders"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Хват значительно шире плеч. Подтягивайтесь к верхней части груди.",
            "technique_en": "Grip significantly wider than shoulders. Pull up to upper chest.",
            "technique_uz": "Yelkadan ancha keng ushlash. Ko'krak yuqori qismiga torting.",
            "common_mistakes_ru": ["Подтягивание подбородком", "Раскачивание", "Недостаточная глубина"],
            "common_mistakes_en": ["Only pulling to chin", "Swinging", "Not deep enough"],
            "common_mistakes_uz": ["Faqat iyag gacha", "Tebranish", "Yetarli chuqur emas"],
            "progression": {
                "beginner": {"sets": 3, "reps": "3-5", "rest_seconds": 150},
                "intermediate": {"sets": 4, "reps": "5-8", "rest_seconds": 120},
                "advanced": {"sets": 5, "reps": "8-12", "rest_seconds": 90}
            }
        },
        "подтягивания_обратным_хватом": {
            "name_ru": "Подтягивания обратным хватом",
            "name_en": "Chin-ups",
            "name_uz": "Teskari ushlash bilan turnikda tortish",
            "muscle_groups": ["biceps", "back"],
            "equipment": "pull_up_bar",
            "difficulty": "beginner",
            "calories_per_rep": 0.9,
            "technique_ru": "Хват на ширине плеч, ладони к себе. Подтягивайтесь мощно, сокращая бицепсы.",
            "technique_en": "Grip shoulder width, palms facing you. Pull up powerfully, contracting biceps.",
            "technique_uz": "Yelka kengligida ushlash, kaftlar o'zingizga qarab. Bicepsni qisqartirib kuchli torting.",
            "common_mistakes_ru": ["Слишком широкий хват", "Раскачивание тела", "Рывки"],
            "common_mistakes_en": ["Grip too wide", "Body swinging", "Jerking movements"],
            "common_mistakes_uz": ["Juda keng ushlash", "Tanani tebratish", "Silkinish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-8", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "12-16", "rest_seconds": 60}
            }
        },
        "подъем_ног_на_турнике": {
            "name_ru": "Подъём ног в висе",
            "name_en": "Hanging leg raises",
            "name_uz": "Osilib turgan holatda oyoqlarni ko'tarish",
            "muscle_groups": ["abs", "core"],
            "equipment": "pull_up_bar",
            "difficulty": "intermediate",
            "calories_per_rep": 0.7,
            "technique_ru": "Висите на турнике. Поднимайте прямые ноги до параллели с полом или выше.",
            "technique_en": "Hang from bar. Raise straight legs to parallel with ground or higher.",
            "technique_uz": "Turnikda osiling. To'g'ri oyoqlarni yer bilan parallel yoki undan balandroq ko'taring.",
            "common_mistakes_ru": ["Раскачивание", "Согнутые колени", "Слишком быстрый темп"],
            "common_mistakes_en": ["Swinging", "Bent knees", "Too fast"],
            "common_mistakes_uz": ["Tebranish", "Bukilgan tizzalar", "Juda tez"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "16-20", "rest_seconds": 60}
            }
        },
        "уголок_на_турнике": {
            "name_ru": "Уголок на турнике",
            "name_en": "L-sit on bar",
            "name_uz": "Turnikda L holatida turish",
            "muscle_groups": ["abs", "core", "shoulders"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_second": 0.2,
            "technique_ru": "Висите на турнике, поднимите прямые ноги до 90° и удерживайте.",
            "technique_en": "Hang from bar, raise straight legs to 90° and hold.",
            "technique_uz": "Turnikda osiling, to'g'ri oyoqlarni 90° ga ko'tarib ushlab turing.",
            "common_mistakes_ru": ["Согнутые ноги", "Раскачивание", "Опускание ног"],
            "common_mistakes_en": ["Bent legs", "Swinging", "Dropping legs"],
            "common_mistakes_uz": ["Oyoqlar bukilgan", "Tebranish", "Oyoqlarni tushirish"],
            "progression": {
                "beginner": {"duration_seconds": 10, "sets": 3, "rest_seconds": 120},
                "intermediate": {"duration_seconds": 20, "sets": 3, "rest_seconds": 90},
                "advanced": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60}
            }
        },
        "выход_силой": {
            "name_ru": "Выход силой на две",
            "name_en": "Muscle-up",
            "name_uz": "Kuch bilan chiqish",
            "muscle_groups": ["back", "chest", "triceps", "shoulders"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 2.0,
            "technique_ru": "Мощный подтягивающий рывок, переход локтями наверх, отжимание.",
            "technique_en": "Powerful pull-up explosion, transition elbows up, press up.",
            "technique_uz": "Kuchli portlatuvchi tortish, tirsak yuqoriga o'tish, surish.",
            "common_mistakes_ru": ["Слишком много раскачивания", "Нет взрывного момента", "Слабый переход"],
            "common_mistakes_en": ["Too much swinging", "No explosive moment", "Weak transition"],
            "common_mistakes_uz": ["Juda ko'p tebranish", "Portlatish yo'q", "Zaif o'tish"],
            "progression": {
                "beginner": {"sets": 2, "reps": "1-3", "rest_seconds": 180},
                "intermediate": {"sets": 3, "reps": "3-5", "rest_seconds": 150},
                "advanced": {"sets": 4, "reps": "5-8", "rest_seconds": 120}
            }
        },
        "австралийские_подтягивания": {
            "name_ru": "Австралийские подтягивания",
            "name_en": "Australian pull-ups",
            "name_uz": "Avstraliya tortishlari",
            "muscle_groups": ["back", "biceps"],
            "equipment": "low_bar",
            "difficulty": "beginner",
            "calories_per_rep": 0.6,
            "technique_ru": "Тело под углом, ноги на полу. Подтягивайте грудь к низкой перекладине.",
            "technique_en": "Body at angle, feet on ground. Pull chest to low bar.",
            "technique_uz": "Tana burchak ostida, oyoqlar yerda. Ko'krakni past turnikga torting.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Неполная амплитуда", "Слишком высокая перекладина"],
            "common_mistakes_en": ["Lower back arch", "Partial ROM", "Bar too high"],
            "common_mistakes_uz": ["Bel egilishi", "To'liq harakat yo'q", "Turnik juda baland"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "20-25", "rest_seconds": 45}
            }
        },
        "подтягивания_за_голову": {
            "name_ru": "Подтягивания за голову",
            "name_en": "Behind neck pull-ups",
            "name_uz": "Bosh orqasiga turnikda tortish",
            "muscle_groups": ["back", "shoulders"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 1.1,
            "technique_ru": "Широкий хват, подтягивайтесь до касания турника затылком.",
            "technique_en": "Wide grip, pull until back of head touches bar.",
            "technique_uz": "Keng ushlash, bosh orqasi turnikka tegguncha torting.",
            "common_mistakes_ru": ["Слишком широкий хват", "Резкие движения", "Недостаточная гибкость плеч"],
            "common_mistakes_en": ["Too wide grip", "Jerky movements", "Insufficient shoulder mobility"],
            "common_mistakes_uz": ["Juda keng ushlash", "Keskin harakatlar", "Yelka harakatchanligi yetarli emas"],
            "progression": {
                "beginner": {"sets": 2, "reps": "3-5", "rest_seconds": 150},
                "intermediate": {"sets": 3, "reps": "5-8", "rest_seconds": 120},
                "advanced": {"sets": 4, "reps": "8-12", "rest_seconds": 90}
            }
        },

        # ============ УПРАЖНЕНИЯ БЕЗ ОБОРУДОВАНИЯ (ДОМА/ЛЕС) ============
        "отжимания_широкие": {
            "name_ru": "Отжимания широким хватом",
            "name_en": "Wide push-ups",
            "name_uz": "Keng qo'yilgan qo'llar bilan poldan turib",
            "muscle_groups": ["chest", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.6,
            "technique_ru": "Руки шире плеч на 20-30см. Опускайтесь медленно, грудью к полу.",
            "technique_en": "Hands 20-30cm wider than shoulders. Lower slowly, chest to floor.",
            "technique_uz": "Qo'llar yelkadan 20-30sm keng. Sekin pastga tushing, ko'krak polga.",
            "common_mistakes_ru": ["Слишком широкая постановка", "Прогиб в пояснице", "Локти слишком в стороны"],
            "common_mistakes_en": ["Hands too wide", "Lower back sag", "Elbows too far out"],
            "common_mistakes_uz": ["Qo'llar juda keng", "Bel egilishi", "Tirsak juda yon tomonga"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "20-25", "rest_seconds": 45}
            }
        },
        "отжимания_узкие": {
            "name_ru": "Отжимания узким хватом (алмазные)",
            "name_en": "Diamond push-ups",
            "name_uz": "Olmossimon poldan turib",
            "muscle_groups": ["triceps", "chest"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.7,
            "technique_ru": "Руки вместе под грудью, пальцы образуют алмаз. Опускайтесь, локти к бокам.",
            "technique_en": "Hands together under chest, fingers form diamond. Lower, elbows to sides.",
            "technique_uz": "Qo'llar ko'krak ostida birgalikda, barmoqlar olmos hosil qiladi. Pastga tushing, tirsak yonlariga.",
            "common_mistakes_ru": ["Локти в стороны", "Слишком быстрый темп", "Неполная амплитуда"],
            "common_mistakes_en": ["Elbows flaring out", "Too fast", "Partial ROM"],
            "common_mistakes_uz": ["Tirsak yonlarga", "Juda tez", "To'liq harakat yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },
        "отжимания_с_наклоном": {
            "name_ru": "Отжимания с ногами на возвышении",
            "name_en": "Decline push-ups",
            "name_uz": "Oyoqlar balandlikda poldan turib",
            "muscle_groups": ["chest", "shoulders"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.8,
            "technique_ru": "Ноги на возвышении (стул, скамья). Опускайтесь до касания грудью пола.",
            "technique_en": "Feet elevated (chair, bench). Lower until chest touches floor.",
            "technique_uz": "Oyoqlar balandlikda (stul, skameyka). Ko'krak polga tegguncha pastga tushing.",
            "common_mistakes_ru": ["Слишком высокое возвышение", "Прогиб поясницы", "Неправильная постановка рук"],
            "common_mistakes_en": ["Elevation too high", "Lower back sag", "Incorrect hand placement"],
            "common_mistakes_uz": ["Juda baland", "Bel egilishi", "Qo'llar noto'g'ri"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 60}
            }
        },
        "планка": {
            "name_ru": "Планка",
            "name_en": "Plank",
            "name_uz": "Planka",
            "muscle_groups": ["core", "abs", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_second": 0.1,
            "technique_ru": "На предплечьях, тело прямое от головы до пяток. Держите корпус напряженным.",
            "technique_en": "On forearms, body straight from head to heels. Keep core tight.",
            "technique_uz": "Bilaklar ustida, tana boshdan tovongacha to'g'ri. O'zakni qattiq ushlab turing.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Поднятый таз", "Опущенная голова"],
            "common_mistakes_en": ["Lower back sag", "Hips too high", "Head dropping"],
            "common_mistakes_uz": ["Bel egilishi", "Son juda baland", "Bosh tushib ketgan"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 60},
                "advanced": {"duration_seconds": 90, "sets": 3, "rest_seconds": 45}
            }
        },
        "боковая_планка": {
            "name_ru": "Боковая планка",
            "name_en": "Side plank",
            "name_uz": "Yon planka",
            "muscle_groups": ["core", "obliques"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_second": 0.12,
            "technique_ru": "На боку, опора на предплечье. Тело прямое, таз поднят.",
            "technique_en": "On side, support on forearm. Body straight, hips up.",
            "technique_uz": "Yonda, bilak ustida tayanch. Tana to'g'ri, son ko'tarilgan.",
            "common_mistakes_ru": ["Опущенный таз", "Скругленная спина", "Неправильная опора"],
            "common_mistakes_en": ["Hips sagging", "Rounded back", "Incorrect support"],
            "common_mistakes_uz": ["Son tushib ketgan", "Orqa egri", "Noto'g'ri tayanch"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45}
            }
        },
        "берпи": {
            "name_ru": "Берпи",
            "name_en": "Burpees",
            "name_uz": "Berpi",
            "muscle_groups": ["cardio", "full_body"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 1.4,
            "technique_ru": "Присед, руки на пол, прыжком ноги назад, отжимание, ноги к рукам, прыжок вверх.",
            "technique_en": "Squat, hands down, jump legs back, push-up, legs to hands, jump up.",
            "technique_uz": "Cho'kkalab, qo'llarni polga, oyoqlarni orqaga sakratib, poldan turib, oyoqlarni qo'llarga, yuqoriga sakrab.",
            "common_mistakes_ru": ["Пропуск отжимания", "Неполный прыжок", "Неправильная техника приседа"],
            "common_mistakes_en": ["Skipping push-up", "Incomplete jump", "Incorrect squat form"],
            "common_mistakes_uz": ["Poldan turibni tashlab ketish", "To'liq sakrash yo'q", "Noto'g'ri cho'kkalash"],
            "progression": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },
        "прыжки_на_месте": {
            "name_ru": "Прыжки на месте",
            "name_en": "Jumping jacks",
            "name_uz": "Joyida sakrash",
            "muscle_groups": ["cardio", "legs", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "Прыжком ноги в стороны, руки через стороны вверх. Обратно в исходное.",
            "technique_en": "Jump feet apart, arms overhead through sides. Back to start.",
            "technique_uz": "Sakrab oyoqlarni yonlarga, qo'llarni yuqoriga. Boshlang'ichga qaytish.",
            "common_mistakes_ru": ["Слишком высокие прыжки", "Неправильная координация", "Сутулость"],
            "common_mistakes_en": ["Jumping too high", "Poor coordination", "Slouching"],
            "common_mistakes_uz": ["Juda baland sakrash", "Noto'g'ri koordinatsiya", "Egrilik"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 90, "sets": 3, "rest_seconds": 30}
            }
        },
        "горный_альпинист": {
            "name_ru": "Горный альпинист",
            "name_en": "Mountain climbers",
            "name_uz": "Tog' alpinisti",
            "muscle_groups": ["core", "cardio", "shoulders"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.3,
            "technique_ru": "Упор лежа, попеременно подтягивайте колени к груди в быстром темпе.",
            "technique_en": "Plank position, alternately drive knees to chest at fast pace.",
            "technique_uz": "Planka holatida, tizzalarni navbatma-navbat ko'krakka tez olib boring.",
            "common_mistakes_ru": ["Поднятый таз", "Медленный темп", "Неполное подтягивание колена"],
            "common_mistakes_en": ["Hips too high", "Too slow", "Incomplete knee drive"],
            "common_mistakes_uz": ["Son juda baland", "Juda sekin", "Tizza to'liq kelmaydi"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 30}
            }
        },
        "приседания_с_прыжком": {
            "name_ru": "Приседания с выпрыгиванием",
            "name_en": "Jump squats",
            "name_uz": "Sakrab cho'kkalash",
            "muscle_groups": ["legs", "glutes", "cardio"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 1.0,
            "technique_ru": "Присядьте, затем мощно выпрыгните вверх. Мягко приземлитесь и повторите.",
            "technique_en": "Squat down, then explosively jump up. Land softly and repeat.",
            "technique_uz": "Cho'kkalab, keyin kuchli yuqoriga sakrang. Yumshoq qo'ning va takrorlang.",
            "common_mistakes_ru": ["Жесткое приземление", "Колени внутрь", "Недостаточная глубина"],
            "common_mistakes_en": ["Hard landing", "Knees caving in", "Insufficient depth"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Tizzalar ichkariga", "Yetarli chuqurlik yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 60}
            }
        },
        "выпады_с_прыжком": {
            "name_ru": "Выпады с прыжком",
            "name_en": "Jump lunges",
            "name_uz": "Sakrash bilan oldinga qadam",
            "muscle_groups": ["legs", "glutes", "cardio"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.9,
            "technique_ru": "Выпад, затем прыжок со сменой ног в воздухе. Приземлитесь в выпад.",
            "technique_en": "Lunge, then jump switching legs in air. Land in lunge.",
            "technique_uz": "Oldinga qadam, keyin sakrab oyoqlarni havoda almashtirish. Oldinga qadam holatida qo'nish.",
            "common_mistakes_ru": ["Жесткое приземление", "Недостаточная амплитуда", "Потеря баланса"],
            "common_mistakes_en": ["Hard landing", "Insufficient ROM", "Loss of balance"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Yetarli harakat yo'q", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-10 на ногу", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-14 на ногу", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "14-18 на ногу", "rest_seconds": 60}
            }
        },
        "приседания_пистолетом": {
            "name_ru": "Приседания на одной ноге (пистолетик)",
            "name_en": "Pistol squats",
            "name_uz": "Bir oyoqda cho'kkalash",
            "muscle_groups": ["legs", "glutes", "core"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Одна нога вперед, приседайте на другой до полной глубины. Вставайте без опоры.",
            "technique_en": "One leg forward, squat on other to full depth. Stand without support.",
            "technique_uz": "Bir oyoq oldinga, boshqasida to'liq chuqurlikka cho'kkalash. Yordam-sisiz turish.",
            "common_mistakes_ru": ["Недостаточная глубина", "Потеря баланса", "Округление спины"],
            "common_mistakes_en": ["Insufficient depth", "Loss of balance", "Rounding back"],
            "common_mistakes_uz": ["Yetarli chuqurlik yo'q", "Balansni yo'qotish", "Orqani egish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "3-5 на ногу", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "5-8 на ногу", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "8-12 на ногу", "rest_seconds": 75}
            }
        },
        "бег_на_месте": {
            "name_ru": "Бег на месте с высоким подниманием колен",
            "name_en": "High knees running",
            "name_uz": "Tizzalarni baland ko'tarib joyida yugurish",
            "muscle_groups": ["cardio", "legs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_second": 0.2,
            "technique_ru": "Бегите на месте, поднимая колени максимально высоко к груди.",
            "technique_en": "Run in place, lifting knees as high as possible to chest.",
            "technique_uz": "Joyida yugurib, tizzalarni iloji boricha ko'krakka ko'taring.",
            "common_mistakes_ru": ["Низкие колени", "Сутулость", "Слишком медленный темп"],
            "common_mistakes_en": ["Low knees", "Slouching", "Too slow pace"],
            "common_mistakes_uz": ["Past tizzalar", "Egrilik", "Juda sekin tezlik"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 30}
            }
        },
        "захлесты_голени": {
            "name_ru": "Захлесты голени",
            "name_en": "Butt kickers",
            "name_uz": "Tovonni dumbasiga urish",
            "muscle_groups": ["cardio", "legs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_second": 0.18,
            "technique_ru": "Бегите на месте, пятками касайтесь ягодиц.",
            "technique_en": "Run in place, heels touching buttocks.",
            "technique_uz": "Joyida yugurib, tovonlar dumbasiga tegsin.",
            "common_mistakes_ru": ["Слишком наклонен корпус", "Пятки не достают", "Слишком медленно"],
            "common_mistakes_en": ["Too much forward lean", "Heels not reaching", "Too slow"],
            "common_mistakes_uz": ["Tanani juda oldinga egish", "Tovonlar yetmaydi", "Juda sekin"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 30}
            }
        },
        "скалолаз_с_паузой": {
            "name_ru": "Скалолаз с паузой",
            "name_en": "Slow mountain climbers",
            "name_uz": "Sekin tog' alpinisti",
            "muscle_groups": ["core", "abs", "legs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.25,
            "technique_ru": "Планка, медленно подтягивайте колено к груди, держите 2 секунды, меняйте.",
            "technique_en": "Plank, slowly bring knee to chest, hold 2 seconds, switch.",
            "technique_uz": "Planka, tizzani sekin ko'krakka olib boring, 2 soniya ushlab turing, almashtiring.",
            "common_mistakes_ru": ["Слишком быстро", "Таз поднят", "Недостаточное подтягивание"],
            "common_mistakes_en": ["Too fast", "Hips up", "Insufficient knee drive"],
            "common_mistakes_uz": ["Juda tez", "Son baland", "Tizza yetarli kelmaydi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12 на ногу", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16 на ногу", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "16-20 на ногу", "rest_seconds": 45}
            }
        },
        "медвежья_походка": {
            "name_ru": "Медвежья походка",
            "name_en": "Bear crawl",
            "name_uz": "Ayiq yurishi",
            "muscle_groups": ["full_body", "core", "shoulders"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_second": 0.15,
            "technique_ru": "На четвереньках, колени над полом. Передвигайтесь вперед, чередуя руки и ноги.",
            "technique_en": "On all fours, knees off ground. Move forward, alternating arms and legs.",
            "technique_uz": "To'rt oyoqda, tizzalar poldan yuqorida. Oldinga yuring, qo'llar va oyoqlarni navbatma-navbat.",
            "common_mistakes_ru": ["Высоко поднятый таз", "Колени на полу", "Слишком быстро"],
            "common_mistakes_en": ["Hips too high", "Knees on floor", "Too fast"],
            "common_mistakes_uz": ["Son juda baland", "Tizzalar polda", "Juda tez"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 75},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 60}
            }
        },
        "крабья_походка": {
            "name_ru": "Крабья походка",
            "name_en": "Crab walk",
            "name_uz": "Qisqichbaqa yurishi",
            "muscle_groups": ["triceps", "core", "glutes"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_second": 0.12,
            "technique_ru": "Сидя, руки сзади, таз поднят. Передвигайтесь вперед/назад.",
            "technique_en": "Sitting, hands behind, hips up. Move forward/backward.",
            "technique_uz": "O'tirgan holatda, qo'llar orqada, son ko'tarilgan. Oldinga/orqaga yuring.",
            "common_mistakes_ru": ["Опущенный таз", "Неправильная опора рук", "Слишком быстро"],
            "common_mistakes_en": ["Hips sagging", "Incorrect hand placement", "Too fast"],
            "common_mistakes_uz": ["Son tushib ketgan", "Qo'llar noto'g'ri", "Juda tez"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45}
            }
        },
        "отжимания_на_кулаках": {
            "name_ru": "Отжимания на кулаках",
            "name_en": "Knuckle push-ups",
            "name_uz": "Mushtlarda poldan turib",
            "muscle_groups": ["chest", "triceps", "wrists"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.6,
            "technique_ru": "Отжимания на кулаках, укрепляет запястья. Тело прямое.",
            "technique_en": "Push-ups on knuckles, strengthens wrists. Body straight.",
            "technique_uz": "Mushtlarda poldan turib, bilakni mustahkamlaydi. Tana to'g'ri.",
            "common_mistakes_ru": ["Слабые кулаки", "Прогиб спины", "Локти в стороны"],
            "common_mistakes_en": ["Weak fists", "Back arching", "Elbows out"],
            "common_mistakes_uz": ["Zaif mushtlar", "Orqa egilgan", "Tirsak yonlarga"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 60}
            }
        },
        "планка_на_одной_руке": {
            "name_ru": "Планка на одной руке",
            "name_en": "Single arm plank",
            "name_uz": "Bir qo'lda planka",
            "muscle_groups": ["core", "abs", "shoulders"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_second": 0.14,
            "technique_ru": "Планка, одну руку за спину. Держите тело стабильным.",
            "technique_en": "Plank, one arm behind back. Keep body stable.",
            "technique_uz": "Planka, bir qo'l orqada. Tanani barqaror ushlab turing.",
            "common_mistakes_ru": ["Поворот корпуса", "Опущенный таз", "Недостаточное время"],
            "common_mistakes_en": ["Torso rotation", "Hips sagging", "Insufficient time"],
            "common_mistakes_uz": ["Tanani burish", "Son tushib ketgan", "Yetarli vaqt yo'q"],
            "progression": {
                "beginner": {"duration_seconds": 15, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 30, "sets": 3, "rest_seconds": 75},
                "advanced": {"duration_seconds": 45, "sets": 3, "rest_seconds": 60}
            }
        },
        "супермен": {
            "name_ru": "Супермен",
            "name_en": "Superman",
            "name_uz": "Superman",
            "muscle_groups": ["back", "glutes", "core"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Лежа на животе, одновременно поднимайте руки и ноги. Держите 2 секунды.",
            "technique_en": "Lying face down, simultaneously lift arms and legs. Hold 2 seconds.",
            "technique_uz": "Yuzing bilan yotib, qo'llar va oyoqlarni bir vaqtda ko'taring. 2 soniya ushlab turing.",
            "common_mistakes_ru": ["Слишком высокий подъем", "Задержка дыхания", "Напряжение шеи"],
            "common_mistakes_en": ["Lifting too high", "Holding breath", "Neck tension"],
            "common_mistakes_uz": ["Juda baland ko'tarish", "Nafasni ushlab turish", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "мост_ягодичный": {
            "name_ru": "Ягодичный мост",
            "name_en": "Glute bridge",
            "name_uz": "Dumba ko'prigi",
            "muscle_groups": ["glutes", "hamstrings", "core"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.4,
            "technique_ru": "Лежа на спине, ноги согнуты. Поднимайте таз вверх, напрягая ягодицы.",
            "technique_en": "Lying on back, knees bent. Lift hips up, squeezing glutes.",
            "technique_uz": "Chalqancha yotib, oyoqlar bukilgan. Sonni yuqoriga ko'tarib, dumbani qisib.",
            "common_mistakes_ru": ["Недостаточный подъем", "Отрыв плеч от пола", "Слишком быстрый темп"],
            "common_mistakes_en": ["Insufficient lift", "Shoulders off floor", "Too fast"],
            "common_mistakes_uz": ["Yetarli ko'tarish yo'q", "Yelka poldan ajralib ketgan", "Juda tez"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "мост_на_одной_ноге": {
            "name_ru": "Ягодичный мост на одной ноге",
            "name_en": "Single leg glute bridge",
            "name_uz": "Bir oyoqda dumba ko'prigi",
            "muscle_groups": ["glutes", "hamstrings", "core"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.6,
            "technique_ru": "Мост, одна нога поднята прямо вверх. Поднимайте таз, напрягая ягодицы.",
            "technique_en": "Bridge, one leg straight up. Lift hips, squeezing glutes.",
            "technique_uz": "Ko'prik, bir oyoq to'g'ri yuqoriga. Sonni ko'tarib, dumbani qisib.",
            "common_mistakes_ru": ["Скручивание таза", "Недостаточная амплитуда", "Опущенная нога"],
            "common_mistakes_en": ["Hip rotation", "Insufficient ROM", "Dropping leg"],
            "common_mistakes_uz": ["Sonni burish", "Yetarli harakat yo'q", "Oyoqni tushirish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12 на ногу", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16 на ногу", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "16-20 на ногу", "rest_seconds": 45}
            }
        },
        "велосипед_лежа": {
            "name_ru": "Велосипед лежа",
            "name_en": "Bicycle crunches",
            "name_uz": "Yotgan holatda velosiped",
            "muscle_groups": ["abs", "obliques"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.25,
            "technique_ru": "Лежа, руки за головой. Подтягивайте колено к противоположному локтю.",
            "technique_en": "Lying down, hands behind head. Bring knee to opposite elbow.",
            "technique_uz": "Yotgan holatda, qo'llar bosh orqasida. Tizzani qarama-qarshi tirsagiga olib boring.",
            "common_mistakes_ru": ["Тянуть шею руками", "Слишком быстро", "Недостаточное скручивание"],
            "common_mistakes_en": ["Pulling neck with hands", "Too fast", "Insufficient rotation"],
            "common_mistakes_uz": ["Bo'yinni qo'llar bilan tortish", "Juda tez", "Yetarli burish yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },
        "скручивания": {
            "name_ru": "Скручивания",
            "name_en": "Crunches",
            "name_uz": "Qorin bosish",
            "muscle_groups": ["abs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "Лежа, ноги согнуты. Поднимайте лопатки от пола, напрягая пресс.",
            "technique_en": "Lying down, knees bent. Lift shoulder blades off floor, contracting abs.",
            "technique_uz": "Yotgan holatda, oyoqlar bukilgan. Yelka suyaklarini poldan ko'tarib, qorinni qisib.",
            "common_mistakes_ru": ["Полный подъем корпуса", "Тянуть шею", "Слишком быстро"],
            "common_mistakes_en": ["Full sit-up", "Pulling neck", "Too fast"],
            "common_mistakes_uz": ["To'liq o'tirib ketish", "Bo'yinni tortish", "Juda tez"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },
        "русские_скручивания": {
            "name_ru": "Русские скручивания",
            "name_en": "Russian twists",
            "name_uz": "Rus burilishlari",
            "muscle_groups": ["abs", "obliques"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.3,
            "technique_ru": "Сидя с поднятыми ногами, поворачивайте корпус в стороны, касаясь пола руками.",
            "technique_en": "Sitting with legs raised, rotate torso side to side, touching floor with hands.",
            "technique_uz": "Oyoqlar ko'tarilgan holatda o'tirib, tanani yonlarga burib, qo'llar bilan polga tegish.",
            "common_mistakes_ru": ["Опущенные ноги", "Недостаточный поворот", "Округленная спина"],
            "common_mistakes_en": ["Legs lowered", "Insufficient rotation", "Rounded back"],
            "common_mistakes_uz": ["Oyoqlar tushib ketgan", "Yetarli burish yo'q", "Orqa egri"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },
        "планка_с_подъемом_ноги": {
            "name_ru": "Планка с подъемом ноги",
            "name_en": "Plank leg lifts",
            "name_uz": "Oyoq ko'tarish bilan planka",
            "muscle_groups": ["core", "glutes", "shoulders"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.35,
            "technique_ru": "Планка, поочередно поднимайте прямые ноги вверх. Держите корпус стабильным.",
            "technique_en": "Plank, alternately lift straight legs up. Keep core stable.",
            "technique_uz": "Planka, to'g'ri oyoqlarni navbatma-navbat yuqoriga ko'taring. O'zakni barqaror ushlab turing.",
            "common_mistakes_ru": ["Поворот таза", "Слишком высокий подъем", "Прогиб спины"],
            "common_mistakes_en": ["Hip rotation", "Lifting too high", "Back arching"],
            "common_mistakes_uz": ["Sonni burish", "Juda baland ko'tarish", "Orqani egish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12 на ногу", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16 на ногу", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "16-20 на ногу", "rest_seconds": 45}
            }
        },
        "отжимания_лучника": {
            "name_ru": "Отжимания лучника",
            "name_en": "Archer push-ups",
            "name_uz": "Kamonchi poldan turib",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 0.9,
            "technique_ru": "Широкая постановка рук. Опускайтесь к одной руке, другая почти прямая.",
            "technique_en": "Wide hand placement. Lower to one arm, other nearly straight.",
            "technique_uz": "Qo'llar keng. Bir qo'lga pastga tushing, boshqasi deyarli to'g'ri.",
            "common_mistakes_ru": ["Слишком быстро", "Недостаточный перенос веса", "Локоть прямой руки согнут"],
            "common_mistakes_en": ["Too fast", "Insufficient weight shift", "Straight arm elbow bent"],
            "common_mistakes_uz": ["Juda tez", "Yetarli og'irlik ko'chirish yo'q", "To'g'ri qo'l tirsagi bukilgan"],
            "progression": {
                "beginner": {"sets": 3, "reps": "4-6 на сторону", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "6-10 на сторону", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "10-14 на сторону", "rest_seconds": 75}
            }
        },
        "отжимания_с_хлопком": {
            "name_ru": "Отжимания с хлопком",
            "name_en": "Clap push-ups",
            "name_uz": "Qarsak chalish bilan poldan turib",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.0,
            "technique_ru": "Мощное отжимание с взрывным выталкиванием. В воздухе хлопок руками.",
            "technique_en": "Powerful push-up with explosive push. Clap hands in air.",
            "technique_uz": "Portlatuvchi surib chiqarish bilan kuchli poldan turib. Havoda qo'llarni qarsak chalish.",
            "common_mistakes_ru": ["Недостаточная мощность", "Жесткое приземление", "Неправильная техника"],
            "common_mistakes_en": ["Insufficient power", "Hard landing", "Incorrect technique"],
            "common_mistakes_uz": ["Yetarli kuch yo'q", "Qattiq qo'nish", "Noto'g'ri texnika"],
            "progression": {
                "beginner": {"sets": 2, "reps": "3-5", "rest_seconds": 150},
                "intermediate": {"sets": 3, "reps": "5-8", "rest_seconds": 120},
                "advanced": {"sets": 4, "reps": "8-12", "rest_seconds": 90}
            }
        },

        # ============ УПРАЖНЕНИЯ С МИНИМАЛЬНЫМ ОБОРУДОВАНИЕМ ============
        "приседания_у_стены": {
            "name_ru": "Приседания у стены (стульчик)",
            "name_en": "Wall sit",
            "name_uz": "Devor yonida stul",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "wall",
            "difficulty": "beginner",
            "calories_per_second": 0.1,
            "technique_ru": "Спиной к стене, опуститесь до угла 90° в коленях. Держите.",
            "technique_en": "Back to wall, lower to 90° knee angle. Hold.",
            "technique_uz": "Devorga orqa, tizzalarda 90° burchakka tushib. Ushlab turing.",
            "common_mistakes_ru": ["Колени выходят за носки", "Недостаточный угол", "Отрыв спины от стены"],
            "common_mistakes_en": ["Knees past toes", "Insufficient angle", "Back off wall"],
            "common_mistakes_uz": ["Tizzalar barmoqlardan o'tadi", "Yetarli burchak yo'q", "Orqa devordan ajralib ketgan"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 75},
                "advanced": {"duration_seconds": 90, "sets": 3, "rest_seconds": 60}
            }
        },
        "отжимания_от_стены": {
            "name_ru": "Отжимания от стены",
            "name_en": "Wall push-ups",
            "name_uz": "Devordan turib",
            "muscle_groups": ["chest", "triceps", "shoulders"],
            "equipment": "wall",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Руки на стене, тело под углом. Сгибайте руки, приближаясь к стене.",
            "technique_en": "Hands on wall, body at angle. Bend arms, moving toward wall.",
            "technique_uz": "Qo'llar devorga, tana burchak ostida. Qo'llarni bukib, devorga yaqinlashing.",
            "common_mistakes_ru": ["Слишком близко к стене", "Прогиб в пояснице", "Неполная амплитуда"],
            "common_mistakes_en": ["Too close to wall", "Lower back arch", "Partial ROM"],
            "common_mistakes_uz": ["Devorga juda yaqin", "Bel egilishi", "To'liq harakat yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "трицепсовые_отжимания_от_стула": {
            "name_ru": "Обратные отжимания от стула",
            "name_en": "Chair dips",
            "name_uz": "Stuldan teskari turib",
            "muscle_groups": ["triceps", "shoulders"],
            "equipment": "chair",
            "difficulty": "beginner",
            "calories_per_rep": 0.5,
            "technique_ru": "Руки на стуле сзади, опускайтесь сгибая локти. Поднимайтесь на трицепсах.",
            "technique_en": "Hands on chair behind, lower by bending elbows. Push up with triceps.",
            "technique_uz": "Qo'llar orqada stulda, tirsaklarni bukib pastga tushing. Triceps bilan ko'taring.",
            "common_mistakes_ru": ["Локти в стороны", "Слишком низкое опускание", "Помощь ногами"],
            "common_mistakes_en": ["Elbows flaring", "Going too low", "Leg assistance"],
            "common_mistakes_uz": ["Tirsak yonlarga", "Juda past tushish", "Oyoqlar bilan yordam"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 45}
            }
        },
        "подъем_на_ступеньку": {
            "name_ru": "Подъем на ступеньку",
            "name_en": "Step-ups",
            "name_uz": "Zinapoyaga chiqish",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "step",
            "difficulty": "beginner",
            "calories_per_rep": 0.5,
            "technique_ru": "Шагайте на возвышение, поднимайтесь силой ноги. Меняйте ноги.",
            "technique_en": "Step onto elevation, rise with leg power. Alternate legs.",
            "technique_uz": "Balandlikka qadam qo'ying, oyoq kuchi bilan ko'tariling. Oyoqlarni almashtiring.",
            "common_mistakes_ru": ["Толчок задней ногой", "Наклон корпуса", "Слишком низкая ступенька"],
            "common_mistakes_en": ["Pushing with back leg", "Leaning torso", "Step too low"],
            "common_mistakes_uz": ["Orqa oyoq bilan itarish", "Tanani egish", "Zinapoya juda past"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15 на ногу", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "15-20 на ногу", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "20-25 на ногу", "rest_seconds": 45}
            }
        },
        "болгарские_сплит_приседания": {
            "name_ru": "Болгарские сплит-приседания",
            "name_en": "Bulgarian split squats",
            "name_uz": "Bolgariya split cho'kkalashlari",
            "muscle_groups": ["legs", "glutes"],
            "equipment": "bench",
            "difficulty": "intermediate",
            "calories_per_rep": 0.8,
            "technique_ru": "Задняя нога на возвышении, приседайте на передней до 90°.",
            "technique_en": "Back foot elevated, squat on front leg to 90°.",
            "technique_uz": "Orqa oyoq balandlikda, old oyoqda 90° ga cho'kkalang.",
            "common_mistakes_ru": ["Колено выходит за носок", "Недостаточная глубина", "Неустойчивость"],
            "common_mistakes_en": ["Knee past toe", "Insufficient depth", "Instability"],
            "common_mistakes_uz": ["Tizza barmoqdan o'tadi", "Yetarli chuqurlik yo'q", "Beqarorlik"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12 на ногу", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16 на ногу", "rest_seconds": 75},
                "advanced": {"sets": 4, "reps": "16-20 на ногу", "rest_seconds": 60}
            }
        },
        "подъем_носков_на_ступеньке": {
            "name_ru": "Подъем на носки на ступеньке",
            "name_en": "Calf raises on step",
            "name_uz": "Zinapoyada tovonlarni ko'tarish",
            "muscle_groups": ["calves"],
            "equipment": "step",
            "difficulty": "beginner",
            "calories_per_rep": 0.15,
            "technique_ru": "Носки на ступеньке, пятки свешены. Поднимайтесь на носки, опускайтесь ниже уровня ступеньки.",
            "technique_en": "Toes on step, heels hanging. Rise on toes, lower below step level.",
            "technique_uz": "Barmoqlar zinapoyada, tovonlar osilib turgan. Barmoqlarda ko'tariling, zinapoya darajasidan pastga tushing.",
            "common_mistakes_ru": ["Недостаточная амплитуда", "Слишком быстрый темп", "Сгибание коленей"],
            "common_mistakes_en": ["Insufficient ROM", "Too fast", "Bending knees"],
            "common_mistakes_uz": ["Yetarli harakat yo'q", "Juda tez", "Tizzalarni bukish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },

        # ============ КАЛИСТЕНИКА И ГИМНАСТИКА ============
        "стойка_на_руках_у_стены": {
            "name_ru": "Стойка на руках у стены",
            "name_en": "Handstand wall hold",
            "name_uz": "Devor yonida qo'llarda turish",
            "muscle_groups": ["shoulders", "core", "arms"],
            "equipment": "wall",
            "difficulty": "advanced",
            "calories_per_second": 0.18,
            "technique_ru": "Киньте ноги на стену, встаньте на руки. Тело прямое, смотрите между рук.",
            "technique_en": "Kick legs to wall, stand on hands. Body straight, look between hands.",
            "technique_uz": "Oyoqlarni devorga olib boring, qo'llarda turing. Tana to'g'ri, qo'llar orasiga qarang.",
            "common_mistakes_ru": ["Прогиб в спине", "Смотреть на стену", "Слишком далеко от стены"],
            "common_mistakes_en": ["Back arching", "Looking at wall", "Too far from wall"],
            "common_mistakes_uz": ["Orqani egish", "Devorga qarash", "Devordan juda uzoq"],
            "progression": {
                "beginner": {"duration_seconds": 15, "sets": 3, "rest_seconds": 120},
                "intermediate": {"duration_seconds": 30, "sets": 3, "rest_seconds": 90},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 75}
            }
        },
        "ласточка": {
            "name_ru": "Ласточка",
            "name_en": "Bird dog",
            "name_uz": "Qushcha",
            "muscle_groups": ["core", "back", "glutes"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.25,
            "technique_ru": "На четвереньках, вытяните разноименные руку и ногу. Держите баланс.",
            "technique_en": "On all fours, extend opposite arm and leg. Hold balance.",
            "technique_uz": "To'rt oyoqda, qarama-qarshi qo'l va oyoqni cho'zing. Balansni ushlab turing.",
            "common_mistakes_ru": ["Скручивание таза", "Опущенная нога", "Потеря баланса"],
            "common_mistakes_en": ["Hip rotation", "Dropping leg", "Loss of balance"],
            "common_mistakes_uz": ["Sonni burish", "Oyoqni tushirish", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15 на сторону", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20 на сторону", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25 на сторону", "rest_seconds": 30}
            }
        },
        "уголок_сидя": {
            "name_ru": "Уголок сидя",
            "name_en": "L-sit",
            "name_uz": "O'tirib L holati",
            "muscle_groups": ["abs", "core", "hip_flexors"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_second": 0.2,
            "technique_ru": "Сидя, руки у бедер. Поднимите прямые ноги, оторвите таз от пола.",
            "technique_en": "Sitting, hands by hips. Lift straight legs, raise hips off floor.",
            "technique_uz": "O'tirgan holatda, qo'llar son yonida. To'g'ri oyoqlarni ko'tarib, sonni poldan ajrating.",
            "common_mistakes_ru": ["Согнутые ноги", "Опущенные плечи", "Недостаточный подъем"],
            "common_mistakes_en": ["Bent legs", "Dropped shoulders", "Insufficient lift"],
            "common_mistakes_uz": ["Oyoqlar bukilgan", "Yelkalar tushib ketgan", "Yetarli ko'tarish yo'q"],
            "progression": {
                "beginner": {"duration_seconds": 10, "sets": 3, "rest_seconds": 120},
                "intermediate": {"duration_seconds": 20, "sets": 3, "rest_seconds": 90},
                "advanced": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60}
            }
        },
        "флаг_дракона": {
            "name_ru": "Флаг дракона",
            "name_en": "Dragon flag",
            "name_uz": "Ajdaho bayrog'i",
            "muscle_groups": ["core", "abs", "back"],
            "equipment": "bench",
            "difficulty": "advanced",
            "calories_per_rep": 1.5,
            "technique_ru": "Лежа, держась за опору над головой. Поднимите все тело прямо, опустите контролируемо.",
            "technique_en": "Lying, holding support above head. Lift entire body straight, lower controlled.",
            "technique_uz": "Yotgan holatda, bosh ustidagi tayanchni ushlab. Butun tanani to'g'ri ko'tarib, nazorat bilan pastga tushiring.",
            "common_mistakes_ru": ["Согнутое тело", "Резкое опускание", "Слабая опора"],
            "common_mistakes_en": ["Bent body", "Dropping fast", "Weak grip"],
            "common_mistakes_uz": ["Tana bukilgan", "Tez tushirish", "Zaif ushlash"],
            "progression": {
                "beginner": {"sets": 2, "reps": "2-4", "rest_seconds": 180},
                "intermediate": {"sets": 3, "reps": "4-6", "rest_seconds": 150},
                "advanced": {"sets": 4, "reps": "6-10", "rest_seconds": 120}
            }
        },
        "передний_вис": {
            "name_ru": "Передний вис",
            "name_en": "Front lever",
            "name_uz": "Old osilib turish",
            "muscle_groups": ["back", "core", "shoulders"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_second": 0.25,
            "technique_ru": "Вис на турнике, тело параллельно полу, руки прямые.",
            "technique_en": "Hang from bar, body parallel to ground, arms straight.",
            "technique_uz": "Turnikda osilib, tana yerga parallel, qo'llar to'g'ri.",
            "common_mistakes_ru": ["Согнутые руки", "Опущенные бедра", "Недостаточное напряжение"],
            "common_mistakes_en": ["Bent arms", "Hips dropping", "Insufficient tension"],
            "common_mistakes_uz": ["Qo'llar bukilgan", "Sonlar tushib ketgan", "Yetarli taranglik yo'q"],
            "progression": {
                "beginner": {"duration_seconds": 5, "sets": 3, "rest_seconds": 150},
                "intermediate": {"duration_seconds": 10, "sets": 3, "rest_seconds": 120},
                "advanced": {"duration_seconds": 15, "sets": 3, "rest_seconds": 90}
            }
        },
        "задний_вис": {
            "name_ru": "Задний вис",
            "name_en": "Back lever",
            "name_uz": "Orqa osilib turish",
            "muscle_groups": ["back", "chest", "shoulders", "core"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_second": 0.22,
            "technique_ru": "Вис спиной вниз, тело параллельно полу.",
            "technique_en": "Hang back down, body parallel to ground.",
            "technique_uz": "Orqa bilan osilib, tana yerga parallel.",
            "common_mistakes_ru": ["Согнутые руки", "Прогиб в пояснице", "Опущенная голова"],
            "common_mistakes_en": ["Bent arms", "Lower back arch", "Head dropping"],
            "common_mistakes_uz": ["Qo'llar bukilgan", "Bel egilishi", "Bosh tushib ketgan"],
            "progression": {
                "beginner": {"duration_seconds": 5, "sets": 3, "rest_seconds": 150},
                "intermediate": {"duration_seconds": 10, "sets": 3, "rest_seconds": 120},
                "advanced": {"duration_seconds": 15, "sets": 3, "rest_seconds": 90}
            }
        },

        # ============ ФУНКЦИОНАЛЬНЫЕ УПРАЖНЕНИЯ ============
        "прыжки_в_длину": {
            "name_ru": "Прыжки в длину с места",
            "name_en": "Standing broad jump",
            "name_uz": "Joyidan uzunlikka sakrash",
            "muscle_groups": ["legs", "glutes", "cardio"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.8,
            "technique_ru": "Присед, мах руками, мощный прыжок вперед. Приземление на обе ноги.",
            "technique_en": "Squat, arm swing, powerful jump forward. Land on both feet.",
            "technique_uz": "Cho'kkalab, qo'llarni silkitib, oldinga kuchli sakrash. Ikkala oyoqqa qo'nish.",
            "common_mistakes_ru": ["Жесткое приземление", "Недостаточный мах руками", "Неполный присед"],
            "common_mistakes_en": ["Hard landing", "Insufficient arm swing", "Incomplete squat"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Yetarli qo'l harakati yo'q", "To'liq cho'kkalash yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "12-15", "rest_seconds": 60}
            }
        },
        "боксерские_прыжки": {
            "name_ru": "Боксерские прыжки",
            "name_en": "Box jumps",
            "name_uz": "Quti ustiga sakrash",
            "muscle_groups": ["legs", "glutes", "cardio"],
            "equipment": "box",
            "difficulty": "intermediate",
            "calories_per_rep": 1.0,
            "technique_ru": "Запрыгивайте на устойчивую возвышенность, спрыгивайте контролируемо.",
            "technique_en": "Jump onto stable elevation, step down controlled.",
            "technique_uz": "Barqaror balandlikka sakrab chiqing, nazorat bilan pastga tushing.",
            "common_mistakes_ru": ["Слишком высокая платформа", "Жесткое приземление", "Спрыгивание вместо схода"],
            "common_mistakes_en": ["Platform too high", "Hard landing", "Jumping down instead of stepping"],
            "common_mistakes_uz": ["Platforma juda baland", "Qattiq qo'nish", "Tushish o'rniga sakrash"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },
        "турецкий_подъем": {
            "name_ru": "Турецкий подъем",
            "name_en": "Turkish get-up",
            "name_uz": "Turk turilishi",
            "muscle_groups": ["full_body", "core", "shoulders"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Лежа, вставайте через серию позиций: на локоть, на руку, на колено, стоя.",
            "technique_en": "Lying down, stand through series: to elbow, to hand, to knee, standing.",
            "technique_uz": "Yotgan holatda, bir qator pozitsiyalar orqali turing: tirsak, qo'l, tizza, turgan.",
            "common_mistakes_ru": ["Слишком быстро", "Неправильная последовательность", "Потеря контроля"],
            "common_mistakes_en": ["Too fast", "Wrong sequence", "Loss of control"],
            "common_mistakes_uz": ["Juda tez", "Noto'g'ri ketma-ketlik", "Nazoratni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "3-5 на сторону", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "5-8 на сторону", "rest_seconds": 90},
                "advanced": {"sets": 4, "reps": "8-12 на сторону", "rest_seconds": 75}
            }
        },
        "фермерская_походка": {
            "name_ru": "Фермерская походка",
            "name_en": "Farmer's walk",
            "name_uz": "Fermer yurishi",
            "muscle_groups": ["full_body", "core", "grip"],
            "equipment": "weights",
            "difficulty": "beginner",
            "calories_per_second": 0.15,
            "technique_ru": "Держите тяжести в руках, идите прямо с напряженным корпусом.",
            "technique_en": "Hold weights in hands, walk straight with tight core.",
            "technique_uz": "Og'irliklarni qo'llarda ushlab, tarang o'zak bilan to'g'ri yuring.",
            "common_mistakes_ru": ["Сутулость", "Слишком тяжелый вес", "Наклон в сторону"],
            "common_mistakes_en": ["Slouching", "Weight too heavy", "Leaning sideways"],
            "common_mistakes_uz": ["Egrilik", "Og'irlik juda og'ir", "Yonga egilish"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 75},
                "advanced": {"duration_seconds": 90, "sets": 3, "rest_seconds": 60}
            }
        },
        "медвежья_ползанье_назад": {
            "name_ru": "Медвежья ползанье назад",
            "name_en": "Bear crawl backward",
            "name_uz": "Ayiq orqaga yurishi",
            "muscle_groups": ["full_body", "core", "coordination"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_second": 0.17,
            "technique_ru": "Медвежья походка, но двигайтесь назад. Сложнее для координации.",
            "technique_en": "Bear crawl but move backward. Harder for coordination.",
            "technique_uz": "Ayiq yurishi, lekin orqaga harakatlaning. Koordinatsiya uchun qiyinroq.",
            "common_mistakes_ru": ["Потеря координации", "Слишком быстро", "Колени на полу"],
            "common_mistakes_en": ["Loss of coordination", "Too fast", "Knees on floor"],
            "common_mistakes_uz": ["Koordinatsiyani yo'qotish", "Juda tez", "Tizzalar polda"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 75},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 60}
            }
        },
        "боковые_прыжки": {
            "name_ru": "Боковые прыжки",
            "name_en": "Lateral jumps",
            "name_uz": "Yonma-yon sakrashlar",
            "muscle_groups": ["legs", "glutes", "cardio"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Прыгайте из стороны в сторону, приземляйтесь мягко на обе ноги.",
            "technique_en": "Jump side to side, land softly on both feet.",
            "technique_uz": "Yonma-yon sakrang, ikkala oyoqqa yumshoq qo'ning.",
            "common_mistakes_ru": ["Жесткое приземление", "Недостаточное расстояние", "Потеря баланса"],
            "common_mistakes_en": ["Hard landing", "Insufficient distance", "Loss of balance"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Yetarli masofa yo'q", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-25", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "25-30", "rest_seconds": 30}
            }
        },
        "конькобежец": {
            "name_ru": "Конькобежец",
            "name_en": "Skater hops",
            "name_uz": "Konkida uchish",
            "muscle_groups": ["legs", "glutes", "cardio", "balance"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.5,
            "technique_ru": "Прыжок в сторону на одну ногу, задняя нога отводится назад.",
            "technique_en": "Hop sideways onto one leg, back leg swings behind.",
            "technique_uz": "Yonga bir oyoqqa sakrab, orqa oyoq orqaga tebriladi.",
            "common_mistakes_ru": ["Недостаточное расстояние", "Потеря баланса", "Жесткое приземление"],
            "common_mistakes_en": ["Insufficient distance", "Loss of balance", "Hard landing"],
            "common_mistakes_uz": ["Yetarli masofa yo'q", "Balansni yo'qotish", "Qattiq qo'nish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15 на сторону", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "15-20 на сторону", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "20-25 на сторону", "rest_seconds": 45}
            }
        },
        "планка_с_касанием_плеч": {
            "name_ru": "Планка с касанием плеч",
            "name_en": "Plank shoulder taps",
            "name_uz": "Yelkaga tegish bilan planka",
            "muscle_groups": ["core", "shoulders", "stability"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.2,
            "technique_ru": "Планка, поочередно касайтесь рукой противоположного плеча.",
            "technique_en": "Plank, alternately tap opposite shoulder with hand.",
            "technique_uz": "Planka, navbatma-navbat qo'l bilan qarama-qarshi yelkaga teging.",
            "common_mistakes_ru": ["Поворот бедер", "Слишком быстро", "Опущенный таз"],
            "common_mistakes_en": ["Hip rotation", "Too fast", "Hips sagging"],
            "common_mistakes_uz": ["Sonni burish", "Juda tez", "Son tushib ketgan"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15 на сторону", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "15-20 на сторону", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "20-25 на сторону", "rest_seconds": 45}
            }
        },
        "планка_с_шагами": {
            "name_ru": "Планка-прогулка",
            "name_en": "Plank walk",
            "name_uz": "Planka-sayr",
            "muscle_groups": ["core", "shoulders", "arms"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.3,
            "technique_ru": "Планка, переходите в упор на ладонях, обратно на предплечья.",
            "technique_en": "Plank, move to hands, back to forearms.",
            "technique_uz": "Planka, qo'llarga o'ting, bilaklar ustiga qaytib.",
            "common_mistakes_ru": ["Качание бедер", "Слишком быстро", "Прогиб спины"],
            "common_mistakes_en": ["Hip swaying", "Too fast", "Back arching"],
            "common_mistakes_uz": ["Sonni tebratish", "Juda tez", "Orqani egish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "16-20", "rest_seconds": 45}
            }
        },
        "прыжки_звездой": {
            "name_ru": "Прыжки звездой",
            "name_en": "Star jumps",
            "name_uz": "Yulduz sakrashlari",
            "muscle_groups": ["cardio", "full_body"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.6,
            "technique_ru": "Присед, выпрыгните с раскрытыми руками и ногами (звездой).",
            "technique_en": "Squat, jump with arms and legs spread (star shape).",
            "technique_uz": "Cho'kkalab, qo'llar va oyoqlar yoyilgan holda sakrang (yulduz shakli).",
            "common_mistakes_ru": ["Жесткое приземление", "Недостаточное раскрытие", "Неполный присед"],
            "common_mistakes_en": ["Hard landing", "Insufficient spread", "Incomplete squat"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Yetarli yoyilish yo'q", "To'liq cho'kkalash yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 75},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 60},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 45}
            }
        },
        "тяга_лицом_к_полу": {
            "name_ru": "Тяга Y на полу",
            "name_en": "Floor Y raise",
            "name_uz": "Polda Y ko'tarish",
            "muscle_groups": ["back", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.15,
            "technique_ru": "Лежа на животе, руки впереди под углом Y. Поднимайте руки от пола.",
            "technique_en": "Lying face down, arms forward in Y angle. Lift arms off floor.",
            "technique_uz": "Yuzing bilan yotib, qo'llar oldinda Y burchagi ostida. Qo'llarni poldan ko'taring.",
            "common_mistakes_ru": ["Подъем головы", "Слишком высоко", "Напряжение шеи"],
            "common_mistakes_en": ["Lifting head", "Too high", "Neck tension"],
            "common_mistakes_uz": ["Boshni ko'tarish", "Juda baland", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "тяга_t_на_полу": {
            "name_ru": "Тяга T на полу",
            "name_en": "Floor T raise",
            "name_uz": "Polda T ko'tarish",
            "muscle_groups": ["back", "shoulders"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.15,
            "technique_ru": "Лежа на животе, руки в стороны (Т). Поднимайте руки от пола.",
            "technique_en": "Lying face down, arms to sides (T). Lift arms off floor.",
            "technique_uz": "Yuzing bilan yotib, qo'llar yonlarda (T). Qo'llarni poldan ko'taring.",
            "common_mistakes_ru": ["Поворот корпуса", "Слишком высоко", "Напряжение шеи"],
            "common_mistakes_en": ["Torso rotation", "Too high", "Neck tension"],
            "common_mistakes_uz": ["Tanani burish", "Juda baland", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_seconds": 30}
            }
        },
        "мертвый_жук": {
            "name_ru": "Мертвый жук",
            "name_en": "Dead bug",
            "name_uz": "O'lik qo'ng'iz",
            "muscle_groups": ["core", "abs"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "Лежа на спине, опускайте разноименные руку и ногу, не отрывая поясницу.",
            "technique_en": "Lying on back, lower opposite arm and leg, keeping lower back down.",
            "technique_uz": "Chalqancha yotib, qarama-qarshi qo'l va oyoqni pastga tushiring, belni poldan ajratmang.",
            "common_mistakes_ru": ["Отрыв поясницы", "Слишком быстро", "Недостаточное опускание"],
            "common_mistakes_en": ["Lower back lifting", "Too fast", "Insufficient lowering"],
            "common_mistakes_uz": ["Belni ko'tarish", "Juda tez", "Yetarli tushirish yo'q"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15 на сторону", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20 на сторону", "rest_seconds": 45},
                "advanced": {"sets": 4, "reps": "20-25 на сторону", "rest_seconds": 30}
            }
        },
        "hollow_hold": {
            "name_ru": "Лодочка",
            "name_en": "Hollow hold",
            "name_uz": "Qayiq",
            "muscle_groups": ["core", "abs"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_second": 0.12,
            "technique_ru": "Лежа на спине, поднимите лопатки и ноги, руки вперед. Поясница прижата.",
            "technique_en": "Lying on back, lift shoulders and legs, arms forward. Lower back pressed down.",
            "technique_uz": "Chalqancha yotib, yelka va oyoqlarni ko'tarib, qo'llar oldinga. Bel polga bosilgan.",
            "common_mistakes_ru": ["Отрыв поясницы", "Слишком высокие ноги", "Согнутые ноги"],
            "common_mistakes_en": ["Lower back lifting", "Legs too high", "Bent legs"],
            "common_mistakes_uz": ["Belni ko'tarish", "Oyoqlar juda baland", "Oyoqlar bukilgan"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45}
            }
        },
        "раскатка_на_коленях": {
            "name_ru": "Раскатка на коленях",
            "name_en": "Ab wheel rollout (knees)",
            "name_uz": "Tizzalarda o'g'irlash",
            "muscle_groups": ["core", "abs", "shoulders"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.6,
            "technique_ru": "На коленях, руки вперед. Катитесь вперед, затем возвращайтесь силой пресса.",
            "technique_en": "On knees, hands forward. Roll forward, return using abs strength.",
            "technique_uz": "Tizzalarda, qo'llar oldinga. Oldinga o'girilib, qorin kuchi bilan qaytib.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Слишком далеко", "Потеря контроля"],
            "common_mistakes_en": ["Lower back sag", "Going too far", "Loss of control"],
            "common_mistakes_uz": ["Bel egilishi", "Juda uzoqqa borish", "Nazoratni yo'qotish"],
            "progression": {
                "beginner": {"sets": 3, "reps": "6-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },

        # ============ ДОПОЛНИТЕЛЬНЫЕ УПРАЖНЕНИЯ С ТУРНИКОМ ============

        "подтягивания_лучник": {
            "name_ru": "Подтягивания лучник",
            "name_en": "Archer pull-ups",
            "name_uz": "Kamonchi tortishlar",
            "muscle_groups": ["back", "biceps", "core"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 1.3,
            "technique_ru": "Подтягивайтесь, смещая вес на одну руку, другую выпрямляя в сторону.",
            "technique_en": "Pull up shifting weight to one arm, extending the other to the side.",
            "technique_uz": "Bir qo'lga og'irlikni o'tkazib torting, ikkinchisini yonga cho'zing.",
            "common_mistakes_ru": ["Резкие движения", "Полное расслабление рук", "Неконтролируемый спуск"],
            "common_mistakes_en": ["Jerky movements", "Complete arm relaxation", "Uncontrolled descent"],
            "common_mistakes_uz": ["Keskin harakatlar", "Qo'llarni to'liq bo'shashtirish", "Nazoratsiz tushish"],
            "progression": {
                "beginner": {"sets": 2, "reps": "2-4", "rest_seconds": 150},
                "intermediate": {"sets": 3, "reps": "4-6", "rest_seconds": 120},
                "advanced": {"sets": 4, "reps": "6-10", "rest_seconds": 90}
            }
        },
        "негативные_подтягивания_одной": {
            "name_ru": "Негативные подтягивания одной рукой",
            "name_en": "One arm negative pull-ups",
            "name_uz": "Bir qo'l negativ tortishlar",
            "muscle_groups": ["back", "biceps", "forearms"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 1.5,
            "technique_ru": "Подпрыгните до верхней точки, медленно опускайтесь на одной руке 5-10 секунд.",
            "technique_en": "Jump to top position, slowly lower on one arm for 5-10 seconds.",
            "technique_uz": "Yuqori nuqtaga sakrang, bir qo'lda 5-10 soniya sekin tushing.",
            "common_mistakes_ru": ["Быстрый спуск", "Полное расслабление", "Слишком высокий прыжок"],
            "common_mistakes_en": ["Fast descent", "Complete relaxation", "Jump too high"],
            "common_mistakes_uz": ["Tez tushish", "To'liq bo'shashish", "Juda baland sakrash"],
            "progression": {
                "beginner": {"sets": 3, "reps": "3-5", "rest_seconds": 180},
                "intermediate": {"sets": 4, "reps": "5-8", "rest_seconds": 150},
                "advanced": {"sets": 5, "reps": "8-12", "rest_seconds": 120}
            }
        },
        "подъем_ног_уголком": {
            "name_ru": "Подъем ног уголком (L-sit raises)",
            "name_en": "L-sit leg raises",
            "name_uz": "L-holat oyoq ko'tarish",
            "muscle_groups": ["abs", "core", "hip_flexors"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 0.9,
            "technique_ru": "В висе удерживайте ноги под углом 90°, поднимайте их к перекладине.",
            "technique_en": "Hanging, hold legs at 90°, raise them towards the bar.",
            "technique_uz": "Osilganingizda oyoqlarni 90° burchakda ushlab turing, panjaraga ko'taring.",
            "common_mistakes_ru": ["Опускание ног ниже 90°", "Раскачка", "Рывковые движения"],
            "common_mistakes_en": ["Legs dropping below 90°", "Swinging", "Jerking motions"],
            "common_mistakes_uz": ["Oyoqlarni 90° dan pastga tushirish", "Chayqalish", "Kuchli harakatlar"],
            "progression": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "12-15", "rest_seconds": 75}
            }
        },
        "подтягивания_коммандо": {
            "name_ru": "Подтягивания коммандо",
            "name_en": "Commando pull-ups",
            "name_uz": "Kommando tortishlar",
            "muscle_groups": ["back", "biceps", "core", "obliques"],
            "equipment": "pull_up_bar",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Хват вдоль перекладины, подтягивайтесь, смещая голову в стороны попеременно.",
            "technique_en": "Grip along the bar, pull up alternating head side to side.",
            "technique_uz": "Panjara bo'ylab ushlab, boshni har galda boshqa tomonga siljitib torting.",
            "common_mistakes_ru": ["Отсутствие контроля", "Резкие движения головой", "Неравномерная нагрузка"],
            "common_mistakes_en": ["Lack of control", "Jerky head movements", "Uneven load"],
            "common_mistakes_uz": ["Nazorat yo'qligi", "Boshning keskin harakati", "Notekis yuk"],
            "progression": {
                "beginner": {"sets": 2, "reps": "4-6", "rest_seconds": 150},
                "intermediate": {"sets": 3, "reps": "6-10", "rest_seconds": 120},
                "advanced": {"sets": 4, "reps": "10-15", "rest_seconds": 90}
            }
        },

        # ============ ПРОДВИНУТЫЕ УПРАЖНЕНИЯ БЕЗ ОБОРУДОВАНИЯ ============

        "отжимания_на_одной_руке": {
            "name_ru": "Отжимания на одной руке",
            "name_en": "One arm push-ups",
            "name_uz": "Bir qo'lda surganish",
            "muscle_groups": ["chest", "triceps", "shoulders", "core"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.8,
            "technique_ru": "Ноги шире плеч, одна рука за спиной. Опускайтесь и поднимайтесь на одной руке.",
            "technique_en": "Feet wider than shoulders, one arm behind back. Lower and push with one arm.",
            "technique_uz": "Oyoqlar yelkadan kengroq, bir qo'l orqada. Bir qo'lda pastga tushing va ko'taring.",
            "common_mistakes_ru": ["Разворот корпуса", "Широкая постановка ног", "Недостаточная амплитуда"],
            "common_mistakes_en": ["Torso rotation", "Legs too wide", "Insufficient range"],
            "common_mistakes_uz": ["Tanani burish", "Oyoqlar juda keng", "Kichik amplituda"],
            "progression": {
                "beginner": {"sets": 2, "reps": "2-4", "rest_seconds": 180},
                "intermediate": {"sets": 3, "reps": "4-8", "rest_seconds": 150},
                "advanced": {"sets": 4, "reps": "8-12", "rest_seconds": 120}
            }
        },
        "пистолетики": {
            "name_ru": "Приседания пистолетиком",
            "name_en": "Pistol squats",
            "name_uz": "To'pponcha o'tirishlar",
            "muscle_groups": ["legs", "glutes", "core", "balance"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Одна нога вперед, приседайте на другой до полного сгиба, вернитесь в исходное положение.",
            "technique_en": "One leg forward, squat on other until full bend, return to start.",
            "technique_uz": "Bir oyoq oldinga, ikkinchisida to'liq bukilguncha o'tiring, boshlanishga qayting.",
            "common_mistakes_ru": ["Потеря баланса", "Колено внутрь", "Опора на пятку"],
            "common_mistakes_en": ["Loss of balance", "Knee inward", "Heel support"],
            "common_mistakes_uz": ["Balansni yo'qotish", "Tizza ichkariga", "Tovoniga suyash"],
            "progression": {
                "beginner": {"sets": 2, "reps": "3-5", "rest_seconds": 120},
                "intermediate": {"sets": 3, "reps": "5-8", "rest_seconds": 90},
                "advanced": {"sets": 4, "reps": "8-12", "rest_seconds": 75}
            }
        },
        "ходьба_на_руках": {
            "name_ru": "Ходьба на руках",
            "name_en": "Handstand walk",
            "name_uz": "Qo'lda yurish",
            "muscle_groups": ["shoulders", "core", "arms", "balance"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 2.0,
            "technique_ru": "Стойка на руках, делайте шаги руками вперед, сохраняя равновесие.",
            "technique_en": "Handstand position, walk forward on hands maintaining balance.",
            "technique_uz": "Qo'lda turish holati, qo'llar bilan oldinga yuring, balansni saqlang.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Слишком быстро", "Потеря баланса"],
            "common_mistakes_en": ["Lower back arch", "Too fast", "Loss of balance"],
            "common_mistakes_uz": ["Belni egish", "Juda tez", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"duration_seconds": 10, "sets": 3, "rest_seconds": 180},
                "intermediate": {"duration_seconds": 20, "sets": 4, "rest_seconds": 150},
                "advanced": {"duration_seconds": 30, "sets": 5, "rest_seconds": 120}
            }
        },
        "планка_на_одной_руке": {
            "name_ru": "Планка на одной руке",
            "name_en": "One arm plank",
            "name_uz": "Bir qo'lda planka",
            "muscle_groups": ["core", "shoulders", "obliques"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 0.4,
            "technique_ru": "Стойка в планке, одну руку за спину, удерживайте позицию.",
            "technique_en": "Plank position, one arm behind back, hold position.",
            "technique_uz": "Planka holatida, bir qo'l orqada, holatni saqlang.",
            "common_mistakes_ru": ["Разворот таза", "Опущенные бедра", "Напряжение шеи"],
            "common_mistakes_en": ["Hip rotation", "Dropped hips", "Neck tension"],
            "common_mistakes_uz": ["Sonni burish", "Sonni tushirish", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"duration_seconds": 15, "sets": 3, "rest_seconds": 90},
                "intermediate": {"duration_seconds": 30, "sets": 4, "rest_seconds": 75},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 60}
            }
        },
        "выходы_силой_на_земле": {
            "name_ru": "Выходы силой на земле (псевдо)",
            "name_en": "Pseudo planche push-ups",
            "name_uz": "Yer ustida kuch chiqishlar",
            "muscle_groups": ["chest", "shoulders", "triceps", "core"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.5,
            "technique_ru": "Руки ниже талии, корпус наклонен вперед. Отжимайтесь с упором на плечи.",
            "technique_en": "Hands below waist, body leaning forward. Push with focus on shoulders.",
            "technique_uz": "Qo'llar beldan pastda, tana oldinga egilgan. Yelkaga e'tibor bilan surging.",
            "common_mistakes_ru": ["Недостаточный наклон", "Разведенные локти", "Прогиб в пояснице"],
            "common_mistakes_en": ["Insufficient lean", "Flared elbows", "Lower back arch"],
            "common_mistakes_uz": ["Yetarli egilish yo'q", "Tirsak keng", "Bel egilishi"],
            "progression": {
                "beginner": {"sets": 2, "reps": "4-6", "rest_seconds": 150},
                "intermediate": {"sets": 3, "reps": "6-10", "rest_seconds": 120},
                "advanced": {"sets": 4, "reps": "10-15", "rest_seconds": 90}
            }
        },

        # ============ УПРАЖНЕНИЯ ДЛЯ ВЗРЫВНОЙ СИЛЫ ============

        "плиометрические_отжимания": {
            "name_ru": "Плиометрические отжимания",
            "name_en": "Plyometric push-ups",
            "name_uz": "Pliometrik surganishlar",
            "muscle_groups": ["chest", "triceps", "shoulders", "power"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 1.2,
            "technique_ru": "Взрывным движением оттолкнитесь от пола так, чтобы руки оторвались.",
            "technique_en": "Explosively push off floor so hands leave the ground.",
            "technique_uz": "Portlovchi harakatda poldan iting, qo'llar yerdan ajralsin.",
            "common_mistakes_ru": ["Мягкое приземление", "Прогиб в пояснице", "Недостаточная мощность"],
            "common_mistakes_en": ["Soft landing", "Lower back arch", "Insufficient power"],
            "common_mistakes_uz": ["Yumshoq qo'nish", "Bel egilishi", "Kuch yetishmasligi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_seconds": 120},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
                "advanced": {"sets": 5, "reps": "12-15", "rest_seconds": 75}
            }
        },
        "прыжки_на_ящик": {
            "name_ru": "Прыжки на ящик",
            "name_en": "Box jumps",
            "name_uz": "Quti ustiga sakrash",
            "muscle_groups": ["legs", "glutes", "power", "calves"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 1.0,
            "technique_ru": "Прыгайте на возвышение, мягко приземляясь на полную стопу.",
            "technique_en": "Jump onto elevation, landing softly on full foot.",
            "technique_uz": "Balandlikka sakrang, to'liq oyoq bilan yumshoq qo'ning.",
            "common_mistakes_ru": ["Жесткое приземление", "Колени внутрь", "Спрыгивание вниз"],
            "common_mistakes_en": ["Hard landing", "Knees inward", "Jumping down"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Tizzalar ichkariga", "Pastga sakrash"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-10", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "10-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },
        "взрывные_выпады": {
            "name_ru": "Взрывные выпады с прыжком",
            "name_en": "Jump lunges",
            "name_uz": "Sakrash bilan portlovchi qadam",
            "muscle_groups": ["legs", "glutes", "power", "cardio"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.9,
            "technique_ru": "Из выпада прыгните вверх, меняя ноги местами в воздухе.",
            "technique_en": "From lunge, jump up switching legs in the air.",
            "technique_uz": "Qadam holatidan sakrab, oyoqlarni havoda almashtiring.",
            "common_mistakes_ru": ["Жесткое приземление", "Колено за носок", "Недостаточная высота"],
            "common_mistakes_en": ["Hard landing", "Knee over toe", "Insufficient height"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Tizza barmoqdan o'tib", "Balandlik yetishmasligi"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-16", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "16-20", "rest_seconds": 60}
            }
        },
        "берпи_с_отжиманием": {
            "name_ru": "Берпи с отжиманием и прыжком",
            "name_en": "Full burpee with push-up",
            "name_uz": "To'liq burpi surganish va sakrash bilan",
            "muscle_groups": ["full_body", "cardio", "power"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 1.5,
            "technique_ru": "Присед, упор лежа, отжимание, прыжок ногами к рукам, выпрыгивание вверх.",
            "technique_en": "Squat, plank, push-up, jump feet to hands, jump up.",
            "technique_uz": "O'tirish, yotish, surganish, oyoqlarni qo'llarga sakratish, yuqoriga sakrash.",
            "common_mistakes_ru": ["Пропуск отжимания", "Неполная амплитуда", "Медленный темп"],
            "common_mistakes_en": ["Skipping push-up", "Incomplete range", "Slow pace"],
            "common_mistakes_uz": ["Surganishni o'tkazib yuborish", "To'liq harakat yo'q", "Sekin temp"],
            "progression": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
                "intermediate": {"sets": 4, "reps": "12-15", "rest_seconds": 75},
                "advanced": {"sets": 5, "reps": "15-20", "rest_seconds": 60}
            }
        },

        # ============ УПРАЖНЕНИЯ НА ГИБКОСТЬ И МОБИЛЬНОСТЬ ============

        "глубокий_присед_с_удержанием": {
            "name_ru": "Глубокий присед с удержанием",
            "name_en": "Deep squat hold",
            "name_uz": "Chuqur o'tirish ushlab turish",
            "muscle_groups": ["legs", "glutes", "mobility", "ankles"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Присядьте максимально глубоко, пятки на полу, удерживайте позицию.",
            "technique_en": "Squat as deep as possible, heels on floor, hold position.",
            "technique_uz": "Imkon qadar chuqur o'tiring, tovon polda, holatni saqlang.",
            "common_mistakes_ru": ["Отрыв пяток", "Округление спины", "Узкая постановка ног"],
            "common_mistakes_en": ["Heels lifting", "Rounded back", "Narrow foot stance"],
            "common_mistakes_uz": ["Tovonni ko'tarish", "Dumaloq orqa", "Tor oyoq qo'yish"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 120, "sets": 3, "rest_seconds": 30}
            }
        },
        "кобра": {
            "name_ru": "Поза кобры",
            "name_en": "Cobra pose",
            "name_uz": "Kobra pozasi",
            "muscle_groups": ["back", "mobility", "spine"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "Лежа на животе, поднимите верх тела на руках, прогибаясь назад.",
            "technique_en": "Lying on stomach, lift upper body on arms, arching back.",
            "technique_uz": "Qorinda yotganingizda, tananing yuqori qismini qo'llarda ko'taring, orqaga eging.",
            "common_mistakes_ru": ["Напряжение плеч", "Сгибание ног", "Чрезмерный прогиб"],
            "common_mistakes_en": ["Shoulder tension", "Bent legs", "Excessive arch"],
            "common_mistakes_uz": ["Yelka tarangligi", "Oyoqlarni bukish", "Haddan tashqari egilish"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 45},
                "intermediate": {"duration_seconds": 40, "sets": 3, "rest_seconds": 30},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 30}
            }
        },
        "собака_мордой_вниз": {
            "name_ru": "Собака мордой вниз",
            "name_en": "Downward dog",
            "name_uz": "Pastga qaragan it",
            "muscle_groups": ["hamstrings", "shoulders", "back", "mobility"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Из упора лежа поднимите таз вверх, образуя треугольник.",
            "technique_en": "From plank raise hips up forming a triangle.",
            "technique_uz": "Plankadan sonni yuqoriga ko'taring, uchburchak hosil qiling.",
            "common_mistakes_ru": ["Согнутые ноги", "Прогиб в пояснице", "Напряжение шеи"],
            "common_mistakes_en": ["Bent legs", "Lower back arch", "Neck tension"],
            "common_mistakes_uz": ["Bukilgan oyoqlar", "Bel egilishi", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 45},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 30},
                "advanced": {"duration_seconds": 90, "sets": 4, "rest_seconds": 30}
            }
        },
        "поза_лягушки": {
            "name_ru": "Поза лягушки",
            "name_en": "Frog pose",
            "name_uz": "Qurbaqa pozasi",
            "muscle_groups": ["hips", "groin", "mobility"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.2,
            "technique_ru": "На коленях, разведите их максимально в стороны, опуститесь на предплечья.",
            "technique_en": "On knees, spread them as wide as possible, lower to forearms.",
            "technique_uz": "Tizzalarda, ularni imkon qadar kengaytiring, bilaklarga tushing.",
            "common_mistakes_ru": ["Резкие движения", "Неравномерная постановка", "Слишком быстро"],
            "common_mistakes_en": ["Jerky movements", "Uneven positioning", "Too fast"],
            "common_mistakes_uz": ["Keskin harakatlar", "Notekis qo'yish", "Juda tez"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 2, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 45},
                "advanced": {"duration_seconds": 120, "sets": 3, "rest_seconds": 30}
            }
        },
        "кошка_корова": {
            "name_ru": "Кошка-корова",
            "name_en": "Cat-cow stretch",
            "name_uz": "Mushuk-sigir cho'zish",
            "muscle_groups": ["back", "spine", "core", "mobility"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "На четвереньках чередуйте прогиб и округление спины.",
            "technique_en": "On all fours, alternate arching and rounding back.",
            "technique_uz": "To'rt oyoqda, orqani egish va yumaloqlashtirish bilan almashinib turing.",
            "common_mistakes_ru": ["Быстрый темп", "Напряжение шеи", "Резкие движения"],
            "common_mistakes_en": ["Fast pace", "Neck tension", "Jerky movements"],
            "common_mistakes_uz": ["Tez temp", "Bo'yin tarangligi", "Keskin harakatlar"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15", "rest_seconds": 45},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 30},
                "advanced": {"sets": 5, "reps": "20-30", "rest_seconds": 30}
            }
        },

        # ============ УПРАЖНЕНИЯ ДЛЯ БАЛАНСА И КООРДИНАЦИИ ============

        "стойка_на_одной_ноге": {
            "name_ru": "Стойка на одной ноге с закрытыми глазами",
            "name_en": "Single leg stand eyes closed",
            "name_uz": "Bir oyoqda ko'z yumib turish",
            "muscle_groups": ["balance", "legs", "core", "ankles"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.2,
            "technique_ru": "Встаньте на одну ногу, закройте глаза, удерживайте баланс.",
            "technique_en": "Stand on one leg, close eyes, hold balance.",
            "technique_uz": "Bir oyoqda turing, ko'zingizni yuming, balansni saqlang.",
            "common_mistakes_ru": ["Открывание глаз", "Напряжение тела", "Дрожь"],
            "common_mistakes_en": ["Opening eyes", "Body tension", "Shaking"],
            "common_mistakes_uz": ["Ko'zni ochish", "Tana tarangligi", "Titr esh"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 30},
                "intermediate": {"duration_seconds": 45, "sets": 3, "rest_seconds": 30},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 20}
            }
        },
        "планка_с_касаниями": {
            "name_ru": "Планка с касаниями плеча",
            "name_en": "Plank shoulder taps",
            "name_uz": "Planka yelka tegish bilan",
            "muscle_groups": ["core", "shoulders", "balance"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.4,
            "technique_ru": "В планке касайтесь поочередно противоположным плечом, не вращая таз.",
            "technique_en": "In plank, tap opposite shoulder alternately without rotating hips.",
            "technique_uz": "Plankada qarama-qarshi yelkaga navbatma-navbat teging, sonni burmaydigan.",
            "common_mistakes_ru": ["Раскачивание таза", "Опущенные бедра", "Быстрый темп"],
            "common_mistakes_en": ["Hip swaying", "Dropped hips", "Fast pace"],
            "common_mistakes_uz": ["Sonni chayqash", "Sonni tushirish", "Tez temp"],
            "progression": {
                "beginner": {"sets": 3, "reps": "16-20", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "20-30", "rest_seconds": 45},
                "advanced": {"sets": 5, "reps": "30-40", "rest_seconds": 30}
            }
        },
        "ходьба_по_линии": {
            "name_ru": "Ходьба по линии пятка-носок",
            "name_en": "Heel-to-toe line walk",
            "name_uz": "Tovon-barmoq chiziqda yurish",
            "muscle_groups": ["balance", "legs", "core", "ankles"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Идите по прямой линии, ставя пятку к носку предыдущей ноги.",
            "technique_en": "Walk straight line, placing heel to toe of previous foot.",
            "technique_uz": "To'g'ri chiziqda yuring, tovonni oldingi oyoqning barmog'iga qo'ying.",
            "common_mistakes_ru": ["Смещение с линии", "Быстрый темп", "Потеря баланса"],
            "common_mistakes_en": ["Shifting off line", "Fast pace", "Loss of balance"],
            "common_mistakes_uz": ["Chiziqdan siljish", "Tez temp", "Balansni yo'qotish"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 45},
                "intermediate": {"duration_seconds": 60, "sets": 3, "rest_seconds": 30},
                "advanced": {"duration_seconds": 90, "sets": 4, "rest_seconds": 30}
            }
        },
        "боковая_планка_с_подъемом_ноги": {
            "name_ru": "Боковая планка с подъемом ноги",
            "name_en": "Side plank leg raise",
            "name_uz": "Yon planka oyoq ko'tarish bilan",
            "muscle_groups": ["obliques", "core", "balance", "hips"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.5,
            "technique_ru": "В боковой планке поднимайте верхнюю ногу вверх, удерживая баланс.",
            "technique_en": "In side plank, raise top leg up while maintaining balance.",
            "technique_uz": "Yon plankada yuqori oyoqni ko'taring, balansni saqlang.",
            "common_mistakes_ru": ["Опущение таза", "Вращение корпуса", "Недостаточная высота"],
            "common_mistakes_en": ["Dropping hips", "Torso rotation", "Insufficient height"],
            "common_mistakes_uz": ["Sonni tushirish", "Tanani burish", "Balandlik yetishmasligi"],
            "progression": {
                "beginner": {"sets": 2, "reps": "8-12", "rest_seconds": 75},
                "intermediate": {"sets": 3, "reps": "12-16", "rest_seconds": 60},
                "advanced": {"sets": 4, "reps": "16-20", "rest_seconds": 45}
            }
        },

        # ============ КОМПЛЕКСНЫЕ ФУНКЦИОНАЛЬНЫЕ УПРАЖНЕНИЯ ============

        "турецкий_подъем_без_веса": {
            "name_ru": "Турецкий подъем без веса",
            "name_en": "Bodyweight Turkish get-up",
            "name_uz": "Tana og'irligi bilan turk ko'tarilish",
            "muscle_groups": ["full_body", "core", "shoulders", "balance"],
            "equipment": "none",
            "difficulty": "advanced",
            "calories_per_rep": 1.2,
            "technique_ru": "Из лежачего положения встаньте, проходя через все фазы турецкого подъема.",
            "technique_en": "From lying position stand up, going through all Turkish get-up phases.",
            "technique_uz": "Yotgan holatdan turk ko'tarilishning barcha bosqichlarini o'tib turing.",
            "common_mistakes_ru": ["Пропуск фаз", "Потеря баланса", "Быстрый темп"],
            "common_mistakes_en": ["Skipping phases", "Loss of balance", "Fast pace"],
            "common_mistakes_uz": ["Bosqichlarni o'tkazib yuborish", "Balansni yo'qotish", "Tez temp"],
            "progression": {
                "beginner": {"sets": 2, "reps": "3-5", "rest_seconds": 120},
                "intermediate": {"sets": 3, "reps": "5-8", "rest_seconds": 90},
                "advanced": {"sets": 4, "reps": "8-10", "rest_seconds": 75}
            }
        },
        "медвежья_походка": {
            "name_ru": "Медвежья походка",
            "name_en": "Bear crawl",
            "name_uz": "Ayiq yurishi",
            "muscle_groups": ["full_body", "shoulders", "core", "cardio"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.8,
            "technique_ru": "На четвереньках с приподнятыми коленями двигайтесь вперед противоположными конечностями.",
            "technique_en": "On all fours with knees lifted, move forward with opposite limbs.",
            "technique_uz": "To'rt oyoqda tizzalar ko'tarilgan holda, qarama-qarshi a'zolarni harakat qiling.",
            "common_mistakes_ru": ["Колени на полу", "Высоко поднятый таз", "Несинхронность"],
            "common_mistakes_en": ["Knees on floor", "Hips too high", "Lack of sync"],
            "common_mistakes_uz": ["Tizzalar polda", "Son juda baland", "Sinxronlash yo'q"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 40, "sets": 4, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 45}
            }
        },
        "краб_ходьба": {
            "name_ru": "Крабья походка",
            "name_en": "Crab walk",
            "name_uz": "Qisqichbaqa yurishi",
            "muscle_groups": ["triceps", "shoulders", "core", "glutes"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.7,
            "technique_ru": "Сидя на ягодицах, поднимите таз и двигайтесь назад на руках и ногах.",
            "technique_en": "Sitting on glutes, lift hips and move backward on hands and feet.",
            "technique_uz": "Dumba ustida o'tirgan holda, sonni ko'taring va qo'l va oyoqlarda orqaga yuring.",
            "common_mistakes_ru": ["Опущенный таз", "Медленный темп", "Колени согнуты"],
            "common_mistakes_en": ["Dropped hips", "Slow pace", "Bent knees"],
            "common_mistakes_uz": ["Tushgan son", "Sekin temp", "Bukilgan tizzalar"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 40, "sets": 4, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 45}
            }
        },
        "прыжки_звездой": {
            "name_ru": "Прыжки звездой",
            "name_en": "Star jumps",
            "name_uz": "Yulduz sakrashlari",
            "muscle_groups": ["full_body", "cardio", "power", "coordination"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.8,
            "technique_ru": "Прыгайте, разводя руки и ноги в стороны, образуя звезду в воздухе.",
            "technique_en": "Jump spreading arms and legs to sides, forming a star in the air.",
            "technique_uz": "Qo'l va oyoqlarni yonlarga tarqatib sakrang, havoda yulduz hosil qiling.",
            "common_mistakes_ru": ["Жесткое приземление", "Недостаточная амплитуда", "Медленный темп"],
            "common_mistakes_en": ["Hard landing", "Insufficient range", "Slow pace"],
            "common_mistakes_uz": ["Qattiq qo'nish", "Amplituda yetishmasligi", "Sekin temp"],
            "progression": {
                "beginner": {"sets": 3, "reps": "10-15", "rest_seconds": 60},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_seconds": 45},
                "advanced": {"sets": 5, "reps": "20-30", "rest_seconds": 30}
            }
        },

        # ============ ИЗОМЕТРИЧЕСКИЕ УПРАЖНЕНИЯ ============

        "стенка_присед": {
            "name_ru": "Стенка (присед у стены)",
            "name_en": "Wall sit",
            "name_uz": "Devor yonida o'tirish",
            "muscle_groups": ["legs", "glutes", "quads", "endurance"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.4,
            "technique_ru": "Спиной к стене, присядьте до угла 90° в коленях, удерживайте позицию.",
            "technique_en": "Back to wall, squat to 90° knee angle, hold position.",
            "technique_uz": "Orqa devorda, tizzada 90° gacha o'tiring, holatni saqlang.",
            "common_mistakes_ru": ["Угол больше 90°", "Отрыв спины от стены", "Стопы слишком близко"],
            "common_mistakes_en": ["Angle over 90°", "Back off wall", "Feet too close"],
            "common_mistakes_uz": ["Burchak 90° dan ko'p", "Orqa devordan uzoq", "Oyoqlar juda yaqin"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 60, "sets": 4, "rest_seconds": 60},
                "advanced": {"duration_seconds": 90, "sets": 4, "rest_seconds": 45}
            }
        },
        "низкая_планка": {
            "name_ru": "Низкая планка (на предплечьях)",
            "name_en": "Low plank (forearm)",
            "name_uz": "Past planka (bilaklar)",
            "muscle_groups": ["core", "abs", "shoulders", "endurance"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Упор на предплечья, тело прямое от головы до пят.",
            "technique_en": "Support on forearms, body straight from head to heels.",
            "technique_uz": "Bilaklar ustida, boshdan tovongacha to'g'ri tana.",
            "common_mistakes_ru": ["Опущенные бедра", "Поднятый таз", "Напряжение шеи"],
            "common_mistakes_en": ["Dropped hips", "Raised hips", "Neck tension"],
            "common_mistakes_uz": ["Tushgan son", "Ko'tarilgan son", "Bo'yin tarangligi"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 4, "rest_seconds": 45},
                "advanced": {"duration_seconds": 120, "sets": 4, "rest_seconds": 30}
            }
        },
        "удержание_полого_тела": {
            "name_ru": "Удержание полого тела",
            "name_en": "Hollow body hold",
            "name_uz": "Bo'sh tana ushlab turish",
            "muscle_groups": ["core", "abs", "hip_flexors"],
            "equipment": "none",
            "difficulty": "intermediate",
            "calories_per_rep": 0.4,
            "technique_ru": "Лежа на спине, поднимите ноги и плечи, руки вперед, поясница прижата к полу.",
            "technique_en": "On back, lift legs and shoulders, arms forward, lower back pressed to floor.",
            "technique_uz": "Orqada yotganingizda, oyoq va yelkalarni ko'taring, qo'llar oldinga, bel polga bosilgan.",
            "common_mistakes_ru": ["Отрыв поясницы", "Согнутые ноги", "Опущенные руки"],
            "common_mistakes_en": ["Lower back lifting", "Bent legs", "Arms dropping"],
            "common_mistakes_uz": ["Belni ko'tarish", "Bukilgan oyoqlar", "Qo'llarni tushirish"],
            "progression": {
                "beginner": {"duration_seconds": 20, "sets": 3, "rest_seconds": 75},
                "intermediate": {"duration_seconds": 40, "sets": 4, "rest_seconds": 60},
                "advanced": {"duration_seconds": 60, "sets": 4, "rest_seconds": 45}
            }
        },
        "мост_ягодичный_удержание": {
            "name_ru": "Ягодичный мост (удержание)",
            "name_en": "Glute bridge hold",
            "name_uz": "Dumba ko'prigi (ushlab turish)",
            "muscle_groups": ["glutes", "hamstrings", "core"],
            "equipment": "none",
            "difficulty": "beginner",
            "calories_per_rep": 0.3,
            "technique_ru": "Лежа на спине, согните ноги, поднимите таз вверх, напрягите ягодицы.",
            "technique_en": "On back, bend legs, lift hips up, squeeze glutes.",
            "technique_uz": "Orqada yotib, oyoqlarni buking, sonni ko'taring, dumbani qisin.",
            "common_mistakes_ru": ["Прогиб в пояснице", "Недостаточная высота", "Расслабленные ягодицы"],
            "common_mistakes_en": ["Lower back arch", "Insufficient height", "Relaxed glutes"],
            "common_mistakes_uz": ["Bel egilishi", "Balandlik yetishmasligi", "Bo'shashgan dumba"],
            "progression": {
                "beginner": {"duration_seconds": 30, "sets": 3, "rest_seconds": 60},
                "intermediate": {"duration_seconds": 60, "sets": 4, "rest_seconds": 45},
                "advanced": {"duration_seconds": 90, "sets": 4, "rest_seconds": 30}
            }
        }
    }

    @classmethod
    def get_exercise(cls, exercise_key: str) -> Optional[dict]:
        """Получить упражнение по ключу"""
        return cls.EXERCISES.get(exercise_key)

    @classmethod
    def search_by_muscle_group(cls, muscle_group: str) -> List[dict]:
        """Найти упражнения для группы мышц"""
        results = []
        for key, exercise in cls.EXERCISES.items():
            if muscle_group in exercise["muscle_groups"]:
                e = exercise.copy()
                e['key'] = key
                results.append(e)
        return results

    @classmethod
    def search_by_equipment(cls, equipment: str) -> List[dict]:
        """Найти упражнения по оборудованию"""
        results = []
        for key, exercise in cls.EXERCISES.items():
            if exercise["equipment"] == equipment:
                e = exercise.copy()
                e['key'] = key
                results.append(e)
        return results

    @classmethod
    def get_all_exercises(cls) -> List[dict]:
        """Получить все упражнения с ключами"""
        results = []
        for key, exercise in cls.EXERCISES.items():
            e = exercise.copy()
            e['key'] = key
            results.append(e)
        return results
