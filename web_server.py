"""
Веб-сервер и деплоер для планов питания
Поддерживает локальный режим и GitHub Pages
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# КОНФИГУРАЦИЯ GitHub Pages
# Установите ваш GitHub username после создания репозитория
GITHUB_USERNAME = "mihh6842-max"
GITHUB_REPO = "avaf"
USE_GITHUB_PAGES = bool(GITHUB_USERNAME)  # Автоматически использовать GitHub Pages если username указан


class PlanHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Обработчик HTTP-запросов для планов питания"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def log_message(self, format, *args):
        """Переопределяем логирование"""
        logger.info(f"Web server: {format % args}")

    def end_headers(self):
        """Добавляем CORS заголовки и заголовок для ngrok"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('ngrok-skip-browser-warning', 'true')
        super().end_headers()


class WebServer:
    """Веб-сервер для планов питания с поддержкой GitHub Pages"""

    def __init__(self, port=8000, use_github_pages=USE_GITHUB_PAGES):
        self.port = port
        self.server = None
        self.thread = None
        self.use_github_pages = use_github_pages
        self.github_username = GITHUB_USERNAME
        self.github_repo = GITHUB_REPO

    def start(self):
        """Запускает веб-сервер в отдельном потоке (только для локальной разработки)"""
        if self.use_github_pages:
            logger.info("✅ Использую GitHub Pages для планов питания")
            logger.info(f"   URL: https://{self.github_username}.github.io/{self.github_repo}/")
            return True

        try:
            self.server = HTTPServer(('localhost', self.port), PlanHTTPRequestHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"✅ Web server started on http://localhost:{self.port}")
            logger.info("⚠️ Локальный режим - планы доступны только на вашем компьютере")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start web server: {e}")
            return False

    def stop(self):
        """Останавливает веб-сервер"""
        if self.server:
            self.server.shutdown()
            logger.info("Web server stopped")

    def get_url(self, filepath: str) -> str:
        """
        Возвращает URL для доступа к файлу

        Args:
            filepath: Путь к файлу (например, 'static/plans/plan_123.html')

        Returns:
            Полный URL
        """
        # Убираем начальный слеш если есть
        if filepath.startswith('/'):
            filepath = filepath[1:]

        # Убираем 'static/' если есть, так как на GitHub Pages это корень
        if filepath.startswith('static/'):
            filepath = filepath[7:]  # len('static/') = 7

        if self.use_github_pages:
            # GitHub Pages URL
            return f"https://{self.github_username}.github.io/{self.github_repo}/{filepath}"
        else:
            # Локальный URL (для тестирования)
            return f"http://localhost:{self.port}/static/{filepath}"

    def get_status(self) -> dict:
        """Получить статус сервера"""
        return {
            "mode": "GitHub Pages" if self.use_github_pages else "Локальный",
            "url_base": f"https://{self.github_username}.github.io/{self.github_repo}/" if self.use_github_pages else f"http://localhost:{self.port}/",
            "ready": True if self.use_github_pages else (self.server is not None)
        }


# Глобальный экземпляр сервера
web_server = WebServer(port=8000)
