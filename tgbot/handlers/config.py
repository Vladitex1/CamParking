import json
from pathlib import Path




# ========== WHITELIST MANAGER ==========
class WhitelistManager:
    user_lvl = ["Неопознано", "Пользователь", "Администратор"]
    def __init__(self, file_path="bin/whitelist.json"):
        self.file_path = Path(file_path)
        self.users = []  # [[user_id, level], ...]
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

    def add_user(self, user_id: int, username: str,firstname: str,lastname: str):
        # Проверяем, нет ли уже пользователя
        for uid, level,un,fn,ln in self.users:
            if uid == user_id:
                return False

        # Добавляем нового пользователя с уровнем 1
        self.users.append([user_id, 1, username, firstname, lastname])
        self.save()
        return True

    def remove_user(self, user_id: int):
        self.users = [[uid, level] for uid, level in self.users if uid != user_id]
        self.save()

    def check_user(self, user_id: int) -> bool:
        for uid, level,un,fn,ln in self.users:
            if uid == user_id:
                return True
        return False

    def check_permission(self, user_id: int):
        for uid, level,un,fn,ln in self.users:
            if uid == user_id:
                return level
        return 0

    async def change_permission(self, user_id: int, permission: int, message):
        for i, (uid, level) in enumerate(self.users):
            if uid == user_id:
                if level == permission:
                    await message.answer("Данные права уже есть у пользователя")
                    return
                self.users[i][1] = permission
                self.save()
                await message.answer(f"Права пользователя {user_id} изменены на {permission}")
                return
        await message.answer("Пользователь не найден")


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

# ========== GLOBAL INSTANCES ==========
whitelist = WhitelistManager()
newusermanager = NewUserslistManager()