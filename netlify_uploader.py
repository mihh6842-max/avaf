"""
Автоматическая загрузка файлов на Netlify через API
"""
import os
import requests
import zipfile
import io

# Netlify настройки - ЗАПОЛНИ ПОСЛЕ ПЕРВОГО ДЕПЛОЯ
NETLIFY_SITE_ID = ""  # Получишь после первого drop
NETLIFY_TOKEN = ""     # Создай на netlify.com/user/applications

def upload_plan_to_netlify(filepath, site_id=None, token=None):
    """
    Загружает новый план на существующий Netlify сайт
    """
    if not site_id or not token:
        print("⚠️ Netlify не настроен. Используй ручной drag&drop")
        return None

    try:
        filename = os.path.basename(filepath)

        # Читаем файл
        with open(filepath, 'rb') as f:
            file_content = f.read()

        # Создаем zip для загрузки
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'plans/{filename}', file_content)

        zip_buffer.seek(0)

        # Netlify API для деплоя
        url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/zip"
        }

        response = requests.post(url, headers=headers, data=zip_buffer.read())

        if response.status_code in [200, 201]:
            deploy = response.json()
            site_url = deploy.get('url', deploy.get('deploy_ssl_url'))
            return f"{site_url}/plans/{filename}"
        else:
            print(f"Ошибка Netlify: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None

if __name__ == "__main__":
    print("Netlify Uploader")
    print("Сначала задеплой вручную через drag&drop, потом настрой автозагрузку")
