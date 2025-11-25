"""
Автоматическая загрузка HTML планов на GitHub Pages
"""
import os
import base64
import requests
import time

# GitHub настройки - ЗАМЕНИ НА СВОИ!
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # Создай на github.com/settings/tokens
GITHUB_REPO = "YOUR_USERNAME/prosport-plans"  # Создай репозиторий
GITHUB_BRANCH = "main"

def upload_plan_to_github(filepath, user_id):
    """Загружает HTML план на GitHub Pages"""
    try:
        filename = os.path.basename(filepath)

        # Читаем файл
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode()

        # GitHub API URL
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/plans/{filename}"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Данные для создания/обновления файла
        data = {
            "message": f"Add nutrition plan for user {user_id}",
            "content": content,
            "branch": GITHUB_BRANCH
        }

        # Отправляем
        response = requests.put(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            # Возвращаем GitHub Pages URL
            return f"https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/plans/{filename}"
        else:
            print(f"Ошибка загрузки: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    print("Скрипт для загрузки планов на GitHub Pages")
    print("Настрой GITHUB_TOKEN и GITHUB_REPO в коде")
