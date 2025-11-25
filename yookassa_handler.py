"""
Модуль для работы с ЮKassa API
Обрабатывает создание платежей и проверку статусов
"""

import uuid
import logging
from typing import Dict, Optional
from yookassa import Configuration, Payment
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

logger = logging.getLogger(__name__)

# Инициализация ЮKassa
if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY
    logger.info("ЮKassa инициализирована успешно")
else:
    logger.warning("ЮKassa ключи не найдены в переменных окружения")


class YooKassaHandler:
    """Обработчик платежей через ЮKassa"""

    @staticmethod
    def create_payment(amount: float, description: str, user_id: int, subscription_key: str, user_email: str = None) -> Optional[Dict]:
        """
        Создает платеж в ЮKassa с чеком согласно 54-ФЗ

        Args:
            amount: Сумма в рублях
            description: Описание платежа
            user_id: ID пользователя Telegram
            subscription_key: Ключ подписки (1_day, 7_days, 14_days)
            user_email: Email пользователя (опционально)

        Returns:
            Dict с данными платежа или None в случае ошибки
        """
        try:
            if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
                logger.error("ЮKassa не настроена - отсутствуют ключи")
                return None

            # Уникальный идентификатор для идемпотентности
            idempotence_key = str(uuid.uuid4())

            # Названия тарифов
            days_map = {
                "1_day": "1 день",
                "7_days": "7 дней",
                "14_days": "14 дней"
            }
            days_text = days_map.get(subscription_key, subscription_key)

            # Формируем данные платежа
            payment_data = {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/FitnessAI_Coach_Bot"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "user_id": str(user_id),
                    "subscription_key": subscription_key
                },
                # Чек согласно 54-ФЗ
                "receipt": {
                    "customer": {
                        "email": user_email if user_email else f"user{user_id}@telegram.user"
                    },
                    "items": [
                        {
                            "description": f"Подписка на фитнес-бота ({days_text})",
                            "quantity": "1.00",
                            "amount": {
                                "value": f"{amount:.2f}",
                                "currency": "RUB"
                            },
                            "vat_code": 1,  # Без НДС
                            "payment_mode": "full_prepayment",  # Предоплата 100%
                            "payment_subject": "service"  # Услуга
                        }
                    ]
                }
            }

            # Создаем платеж
            payment = Payment.create(payment_data, idempotence_key)

            logger.info(f"Создан платеж {payment.id} для пользователя {user_id}")

            return {
                "id": payment.id,
                "status": payment.status,
                "confirmation_url": payment.confirmation.confirmation_url,
                "amount": amount,
                "description": description
            }

        except Exception as e:
            logger.error(f"Ошибка создания платежа ЮKassa: {e}")
            return None

    @staticmethod
    def check_payment(payment_id: str) -> Optional[Dict]:
        """
        Проверяет статус платежа

        Args:
            payment_id: ID платежа в ЮKassa

        Returns:
            Dict с данными платежа или None
        """
        try:
            payment = Payment.find_one(payment_id)

            return {
                "id": payment.id,
                "status": payment.status,
                "paid": payment.paid,
                "amount": float(payment.amount.value),
                "metadata": payment.metadata
            }

        except Exception as e:
            logger.error(f"Ошибка проверки платежа {payment_id}: {e}")
            return None

    @staticmethod
    def is_payment_successful(payment_id: str) -> bool:
        """
        Проверяет, успешно ли прошел платеж

        Args:
            payment_id: ID платежа

        Returns:
            True если платеж успешен
        """
        payment_data = YooKassaHandler.check_payment(payment_id)
        if payment_data:
            return payment_data.get("status") == "succeeded" and payment_data.get("paid", False)
        return False


# Для хранения временных данных о платежах
pending_payments = {}

def store_pending_payment(user_id: int, payment_id: str, subscription_key: str):
    """Сохраняет информацию о незавершенном платеже"""
    pending_payments[payment_id] = {
        "user_id": user_id,
        "subscription_key": subscription_key
    }

def get_pending_payment(payment_id: str) -> Optional[Dict]:
    """Получает информацию о платеже"""
    return pending_payments.get(payment_id)

def remove_pending_payment(payment_id: str):
    """Удаляет информацию о платеже"""
    if payment_id in pending_payments:
        del pending_payments[payment_id]
