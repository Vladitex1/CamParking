import json
from pathlib import Path
from aiogram import Bot
from aiogram import Router, types, F
#sqlite
#######################СЛОМАНЫЙ ПЕРЕХОД ПРИ недостатке прав
# ========== WHITELIST MANAGER ==========
import sqlite3
from pathlib import Path


class WhitelistManager:
    user_lvl = ["Неопознано", "Пользователь", "Администратор"]

    def __init__(self, db_path="bin/whitelist.db"):
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """Создаем таблицу если её нет"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    username TEXT,
                    firstname TEXT,
                    lastname TEXT
                )
            """)

    def load(self):
        """Загружаем всех пользователей из БД"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, level, username, firstname, lastname FROM users")
            self.users = cursor.fetchall()

    def save(self):
        """Метод для совместимости с вашим кодом"""
        pass  # В SQLite сохранение происходит сразу при добавлении/изменении

    def add_user(self, user_id: int, username: str, firstname: str, lastname: str):
        """Добавляем нового пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Проверяем есть ли уже пользователь
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return False

            # Добавляем нового
            cursor.execute("""
                INSERT INTO users (user_id, level, username, firstname, lastname)
                VALUES (?, 1, ?, ?, ?)
            """, (user_id, username, firstname, lastname))
            conn.commit()
            return True

    def delete_user(self, user_id: int, my_user_id: int):
        """Удаляем пользователя"""
        if user_id == my_user_id:
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def check_user(self, user_id: int) -> bool:
        """Проверяем есть ли пользователь в белом списке"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None

    def check_permission(self, user_id: int):
        """Ищем сколько прав у пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def valid_user_permissions(self, user_id: int, target_level: int):
        """Соответствует ли юзер правам да/нет"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                user_level = result[0]
                return target_level <= user_level
            return False

    def get_user_data(self, user_id: int):
        """Получаем данные пользователя"""
        self.load()
        for num, (uid, level, un, fn, ln) in enumerate(self.users):
            if uid == user_id:
                return num + 1, level, un, fn, ln
        return None

    def change_permission(self, user_id: int, permission: int):
        """Изменяем права пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Проверяем текущие права
            cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if not result or result[0] == permission:
                return False

            # Меняем права
            cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (permission, user_id))
            conn.commit()
            return True


# ========== NEW USERS MANAGER ==========
class NewUserslistManager:
    def __init__(self, file_path="bin/newuserslist.json"):
        self.file_path = Path(file_path)
        self.users = []  # [[user_id, username, firstname, lastname], ...]
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = []

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.users, f)

    def approve_user(self, user_id: int, username: str, firstname: str, lastname: str):
        # Проверяем, нет ли уже такого пользователя
        for uid, un, fn, ln in self.users:
            if uid == user_id:
                return False

        # Добавляем нового
        self.users.append([user_id, username or "", firstname or "", lastname or ""])
        self.save()
        return True

    def remove_new_user(self, user_id: int):
        for num, (uid, un, fn, ln) in enumerate(self.users):
            if uid == user_id:
                self.users.pop(num)
        self.save()

    def check_user(self, user_id: int) -> bool:
        for uid, un, fn, ln in self.users:
            if uid == user_id:
                return True
        return False

    def all_about_new_user(self,user_id: int):
        for uid, un, fn, ln in self.users:
            if uid == user_id:
                return [uid, un, fn, ln]

# ========== HANDLER MANAGER ==========

class HandlerManager:
    async def del_messages(self,target_num: int, bot: Bot, message: types.Message):
        """Удаляет последние target_num сообщений в чате, начиная с текущего."""

        chat_id = message.chat.id
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message.message_id - target_num
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение {message.message_id - target_num}: {e}")


# ========== GLOBAL INSTANCES ==========
whitelist = WhitelistManager()
newusermanager = NewUserslistManager()
handlermanager = HandlerManager()