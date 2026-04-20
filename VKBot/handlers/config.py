import json
import sqlite3
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WhitelistManager:
    """Менеджер белого списка пользователей с кэшированием"""
    user_lvl = ["Неопознано", "Пользователь", "Админ"]
    user_lvl_icon = ["👤", "👨‍💼", "👑"]

    def __init__(self, db_path="db/whitelist.db"):
        self.default_mask = 'None'
        self.default_config = 'None'
        self.default_ip = "None"
        self.default_letters = "0"
        self.default_user_mask = "None"
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        #self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path, timeout=10.0) as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    username TEXT,
                    firstname TEXT,
                    lastname TEXT,
                    mask TEXT DEFAULT '{self.default_mask}',
                    config TEXT DEFAULT '{self.default_config}',
                    ip TEXT DEFAULT '{self.default_ip}',
                    letters TEXT DEFAULT '{self.default_letters}',
                    user_mask_slot_1 TEXT DEFAULT '{self.default_user_mask}'
                )
            """)
            self.ensure_columns(conn)

    def ensure_columns(self, conn: sqlite3.Connection):
        """Добавляет недостающие колонки в существующую таблицу users."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {
            "ip": f"ALTER TABLE users ADD COLUMN ip TEXT DEFAULT '{self.default_ip}'",
            "letters": f"ALTER TABLE users ADD COLUMN letters TEXT DEFAULT '{self.default_letters}'",
            "user_mask_slot_1": f"ALTER TABLE users ADD COLUMN user_mask_slot_1 TEXT DEFAULT '{self.default_user_mask}'",
        }

        for column_name, alter_query in expected_columns.items():
            if column_name not in existing_columns:
                conn.execute(alter_query)

    def check_user(self, user_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None

    def check_permission(self, user_id: int) -> int:
        """Возвращает уровень доступа пользователя (level) или 0, если не найден."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            return res[0] if res else 0

    def get_settings(self, setting_name: str, user_id: int):
        """Возвращает значение конкретной колонки настроек для пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {setting_name} FROM users WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            return res[0] if res else None

    def get_user_data(self, user_id: int):
        """Возвращает кортеж данных пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, level, username, firstname, lastname FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def add_user(self, user_id: int, username: str, firstname: str, lastname: str, level: int = 1):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO users (user_id, level, username, firstname, lastname) VALUES (?, ?, ?, ?, ?)",
                (user_id, level, username, firstname, lastname)
            )

    def valid_user_permissions(self, user_id: int, required_level: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            return res is not None and res[0] >= required_level

    def set_settings(self, setting_name: str, user_id: int, value):
        """Устанавливает значение конкретной колонки настроек для пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            # Параметризованный запрос для безопасности
            conn.execute(
                f"UPDATE users SET {setting_name} = ? WHERE user_id = ?",
                (value, user_id)
            )
            conn.commit()

    def get_user_list(self):
        """Возвращает список всех пользователей для админки."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, level, username, firstname, lastname FROM users")
            return cursor.fetchall()

    def delete_user(self, target_id: int, actor_id: int) -> bool:
        """Удаляет пользователя из вайтлиста, не позволяя удалить самого себя."""
        if target_id == actor_id:
            return False
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM users WHERE user_id = ?", (target_id,))
        return True

    def change_permission(self, target_id: int, new_level: int) -> bool:
        """Меняет уровень доступа пользователя."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE users SET level = ? WHERE user_id = ?", (new_level, target_id))
        return True

# Оставляем UserManager как был или добавь методы сохранения в JSON по аналогии
class UserManager:
    def __init__(self, file_path="db/new_users.json"):
        self.file_path = Path(file_path)
        self.users = []
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.users = json.load(f)

    def save(self, force=False):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)

    def add_new_user(self, user_id, username, firstname, lastname):
        if not any(u[0] == user_id for u in self.users):
            self.users.append([user_id, username, firstname, lastname])
            self.save()
            return True
        return False

    def remove_new_user(self, user_id: int):
        self.users = [u for u in self.users if u[0] != user_id]
        self.save()

    def all_about_new_user(self, user_id: int):
        for u in self.users:
            if u[0] == user_id:
                return u
        return None

    def approve_user(self, user_id, username, firstname, lastname):
        """Добавляет нового пользователя в список заявок. Возвращает True, если добавлен впервые."""
        return self.add_new_user(user_id, username, firstname, lastname)

    def check_user(self, user_id: int) -> bool:
        """Проверяет, есть ли пользователь в списке заявок."""
        return self.all_about_new_user(user_id) is not None

    def del_all(self):
        """Очищает список заявок на доступ."""
        self.users = []
        self.save()

whitelist = WhitelistManager()
usermanager = UserManager()