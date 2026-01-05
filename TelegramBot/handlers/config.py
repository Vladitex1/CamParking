import json
import sqlite3
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ========== WHITELIST MANAGER ==========
class WhitelistManager:
    """Менеджер белого списка пользователей с кэшированием"""

    # Уровни доступа пользователей
    user_lvl = ["Неопознано", "Пользователь", "Администратор"]
    user_lvl_icon = ["👤", "👨‍💼", "👑"]

    def __init__(self, db_path="db/whitelist.db"):
        """
        Инициализация менеджера.

        Args:
            db_path: путь к файлу базы данных SQLite
        """
        self.db_path = Path(db_path)
        self._cache = {}  # Кэш в памяти
        self._cache_ttl = 30  # Время жизни кэша в секундах
        self.init_db()

    # ========== ОБЪЯСНЕНИЕ КЭША ==========
    def init_db(self):
        """Создаем таблицу если её нет"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    username TEXT,
                    firstname TEXT,
                    lastname TEXT
                )
            """)

    def _update_cache(self, user_id: int, level: int, exists: bool):
        """Обновляем кэш для пользователя"""
        self._cache[user_id] = (level, time.time(), exists)

    def _get_from_cache(self, user_id: int):
        """Получаем данные из кэша (если актуальны)"""
        if user_id in self._cache:
            level, timestamp, exists = self._cache[user_id]
            if time.time() - timestamp < self._cache_ttl:
                return level, exists
        return None

    def check_user(self, user_id: int) -> bool:
        """
        Проверяем есть ли пользователь в белом списке.
        Использует двухуровневую проверку: кэш → БД
        """
        # 1. Пробуем взять из кэша
        cached = self._get_from_cache(user_id)
        if cached is not None:
            level, exists = cached
            return exists

        # 2. Если нет в кэше или устарел - идем в БД
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            exists = result is not None
            level = result[0] if result else 0

            # 3. Сохраняем в кэш (даже если пользователя нет!)
            self._update_cache(user_id, level, exists)
            return exists

    def check_permission(self, user_id: int) -> int:
        """Получаем уровень доступа пользователя"""
        # 1. Пробуем из кэша
        cached = self._get_from_cache(user_id)
        if cached is not None:
            level, exists = cached
            return level if exists else 0

        # 2. Идем в БД
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                level = result[0]
                self._update_cache(user_id, level, True)
                return level

            # Пользователь не найден
            self._update_cache(user_id, 0, False)
            return 0

    def valid_user_permissions(self, user_id: int, target_level: int) -> bool:
        """Проверяем, достаточно ли прав у пользователя"""
        user_level = self.check_permission(user_id)
        return target_level <= user_level

    def get_user_list(self):
        """Получаем всех пользователей из БД (без кэширования)"""
        start_time = time.time()
        logger.debug("🔄 Whitelist.get_user_list() начат")

        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, level, username, firstname, lastname 
                    FROM users 
                    ORDER BY user_id
                """)
                result = cursor.fetchall()

                elapsed = time.time() - start_time
                logger.debug(f"✅ Whitelist.get_user_list() завершен за {elapsed:.2f}с")
                return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Whitelist.get_user_list() ошибка: {e}")
            return []

    def get_user_data(self, user_id: int):
        """Получаем полные данные пользователя по ID"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, level, username, firstname, lastname 
                FROM users WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()  # Возвращает кортеж или None

    def add_user(self, user_id: int, username: str, firstname: str, lastname: str) -> bool:
        """Добавляем нового пользователя"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()

            # Проверяем существует ли уже
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return False  # Уже существует

            # Добавляем нового
            cursor.execute("""
                INSERT INTO users (user_id, level, username, firstname, lastname)
                VALUES (?, 1, ?, ?, ?)
            """, (user_id, username or "", firstname or "", lastname or ""))
            conn.commit()

            # ОБНОВЛЯЕМ КЭШ - важно!
            self._update_cache(user_id, 1, True)
            return True

    def delete_user(self, user_id: int, my_user_id: int) -> bool:
        """Удаляем пользователя (нельзя удалить себя)"""
        if user_id == my_user_id:
            return False

        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            deleted = cursor.rowcount > 0

            # ОЧИЩАЕМ КЭШ если пользователь удален
            if deleted:
                self._cache.pop(user_id, None)
            return deleted

    def change_permission(self, user_id: int, permission: int) -> bool:
        """Изменяем права пользователя"""
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            cursor = conn.cursor()

            # Проверяем текущие права
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if not result or result[0] == permission:
                return False  # Не найден или права те же

            # Обновляем
            cursor.execute("UPDATE users SET level = ? WHERE user_id = ?",
                           (permission, user_id))
            conn.commit()

            # ОБНОВЛЯЕМ КЭШ
            if user_id in self._cache:
                old_level, timestamp, exists = self._cache[user_id]
                self._update_cache(user_id, permission, exists)

            return True

    def clear_cache(self):
        """Очищаем весь кэш (пригодится для отладки)"""
        self._cache.clear()
        logger.debug("🧹 Кэш Whitelist очищен")


# ========== NEW USERS MANAGER ==========
class UserslistManager:
    """Менеджер заявок новых пользователей (JSON-хранилище)"""

    def __init__(self, file_path="db/newuserslist.json"):
        self.file_path = Path(file_path)
        self.users = []  # [[user_id, username, firstname, lastname], ...]
        self._last_save = 0
        self.save_delay = 2  # Минимальная задержка между сохранениями
        self.load()

    def load(self):
        """Загружаем данные из файла"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки {self.file_path}: {e}")
                self.users = []
        else:
            self.users = []

    def save(self, force=False):
        """
        Сохраняем данные в файл с задержкой.

        Args:
            force: если True, сохраняем сразу, иначе с задержкой
        """
        current_time = time.time()
        if not force and current_time - self._last_save < self.save_delay:
            return  # Слишком рано для сохранения

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            self._last_save = current_time
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения {self.file_path}: {e}")

    def approve_user(self, user_id: int, username: str, firstname: str, lastname: str) -> bool:
        """
        Добавляем заявку пользователя.
        Возвращает False если заявка уже существует.
        """
        for uid, un, fn, ln in self.users:
            if uid == user_id:
                return False  # Уже есть заявка

        self.users.append([
            user_id,
            username or "",
            firstname or "",
            lastname or ""
        ])
        self.save(force=True)  # Важное изменение - сохраняем сразу
        return True

    def remove_new_user(self, user_id: int):
        """Удаляем заявку пользователя"""
        for i, (uid, un, fn, ln) in enumerate(self.users):
            if uid == user_id:
                self.users.pop(i)
                self.save(force=True)
                return
        self.save()  # На всякий случай сохраняем

    def check_user(self, user_id: int) -> bool:
        """Проверяем есть ли заявка от пользователя"""
        return any(uid == user_id for uid, _, _, _ in self.users)

    def all_about_new_user(self, user_id: int):
        """
        Получаем все данные о заявке пользователя.
        Возвращает кортеж (user_id, username, firstname, lastname) или None.
        """
        for uid, un, fn, ln in self.users:
            if uid == user_id:
                return uid, un, fn, ln  # КОРТЕЖ из 4 элементов
        return None  # Только None, не кортеж!

    def del_all(self):
        self.users = []
        self.save()  # На всякий случай сохраняем

# ========== GLOBAL INSTANCES ==========
# Создаем единственные экземпляры для использования во всем проекте
whitelist = WhitelistManager()
usermanager = UserslistManager()
