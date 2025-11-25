# ProSport - Фитнес-бот

Telegram-бот для фитнеса с персональными планами питания, тренировками и AI-чатом.

## Возможности

- Персональные планы питания с HTML-визуализацией
- Программы тренировок
- Трекинг воды и достижения
- AI-чат (OpenRouter)
- 3 языка: RU, EN, UZ

## Запуск

```bash
pip install -r requirements.txt
python l.py
```

## Настройка GitHub Pages

### 1. Создайте публичный репозиторий на GitHub

```
https://github.com/new
Имя: prosport
Public ✓
```

### 2. Привяжите репозиторий

```bash
git remote add origin https://github.com/YOUR-USERNAME/prosport.git
git push -u origin master
```

### 3. Включите GitHub Pages

```
Settings → Pages → Source: GitHub Actions
```

### 4. Укажите username в web_server.py

```python
GITHUB_USERNAME = "your-username"
```

### 5. Запушьте изменения

```bash
git add web_server.py
git commit -m "Configure GitHub Pages"
git push
```

Готово! Планы будут доступны на `https://your-username.github.io/prosport/`
