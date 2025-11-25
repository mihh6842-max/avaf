"""
Автоматический деплой планов на GitHub Pages
Использует GitHub Actions для автоматической публикации
"""
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

class GitHubPagesDeployer:
    def __init__(self, username: str = "", repo_name: str = "prosport"):
        """
        Инициализация деплоера

        Args:
            username: GitHub username (заполнить после создания репозитория)
            repo_name: Имя репозитория на GitHub
        """
        self.username = username
        self.repo_name = repo_name
        self.base_url = f"https://{username}.github.io/{repo_name}" if username else ""

    def get_plan_url(self, filename: str) -> str:
        """
        Получить URL для плана питания

        Args:
            filename: Имя файла (например, plan_123_456.html)

        Returns:
            Полный URL к файлу на GitHub Pages
        """
        if not self.base_url:
            return "https://YOUR-USERNAME.github.io/prosport/plans/" + filename
        return f"{self.base_url}/plans/{filename}"

    def is_git_repo(self) -> bool:
        """Проверить, является ли текущая директория git репозиторием"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def has_remote(self) -> bool:
        """Проверить, настроен ли remote origin"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def commit_and_push(self, file_path: str, message: Optional[str] = None) -> bool:
        """
        Добавить файл в git и запушить на GitHub

        Args:
            file_path: Путь к файлу относительно корня проекта
            message: Сообщение коммита

        Returns:
            True если успешно, False если ошибка
        """
        try:
            if not self.is_git_repo():
                print("❌ Не git репозиторий. Сначала выполните: git init")
                return False

            if not self.has_remote():
                print("⚠️ Remote origin не настроен. Добавьте репозиторий на GitHub")
                return False

            # Добавить файл
            subprocess.run(["git", "add", file_path], check=True)

            # Коммит
            commit_msg = message or f"Add plan {Path(file_path).name}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            # Push
            subprocess.run(["git", "push"], check=True)

            print(f"✅ Файл {file_path} успешно запушен на GitHub")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при деплое: {e}")
            return False

    def setup_instructions(self):
        """Вывести инструкции по настройке"""
        try:
            # Попытка установить UTF-8 для Windows
            import sys
            if sys.platform == 'win32':
                import io
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except:
            pass

        print("=" * 60)
        print("INSTRUKCIYA PO NASTROIKE GITHUB PAGES")
        print("=" * 60)
        print()
        print("1. Sozdaite repozitoriy na GitHub:")
        print("   - Otkroite https://github.com/new")
        print(f"   - Imya: {self.repo_name}")
        print("   - Public (publichnyj)")
        print()
        print("2. Privyazhite lokalnyj repozitoriy:")
        print("   git remote add origin https://github.com/YOUR-USERNAME/prosport.git")
        print("   git branch -M master")
        print("   git push -u origin master")
        print()
        print("3. Vklyuchite GitHub Pages:")
        print("   - Settings -> Pages -> Source: GitHub Actions")
        print()
        print("4. Obnovite username v web_server.py:")
        print("   GITHUB_USERNAME = 'YOUR-USERNAME'")
        print()
        print("5. GitHub Actions avtomaticheski zadeploit pri push")
        print()
        print("=" * 60)
        print()
        print("Podrobnaya instrukciya: sm. GITHUB_SETUP.md")
        print("Bystraya nastroika: sm. QUICK_START_GITHUB.md")


# Глобальный экземпляр
deployer = GitHubPagesDeployer()


if __name__ == "__main__":
    deployer.setup_instructions()
