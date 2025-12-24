import json
from pathlib import Path
from aiogram import Bot
from aiogram import Router, types, F

#######################СЛОМАНЫЙ ПЕРЕХОД ПРИ недостатке прав
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

    def delete_user(self, user_id: int,my_user_id:int):
        for num, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id:
                if uid != my_user_id:
                    self.load()
                    self.users.pop(num)
                else:
                    return False
        self.save()
        return True

    #### если пользователь в вайтлисте
    def check_user(self, user_id: int) -> bool:
        for num, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id:
                return True
        return False

    ### ищет сколько прав у пользователя
    def check_permission(self, user_id: int):
        for num, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id:
                return level
        return 0

    ### соответствует ли юзер правам да/нет
    def valid_user_permissions(self,user_id: int,target_level:int):
        for num, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id: #если находит человека в вайтлисте / нет = false
                if target_level <= level: #если заданный уровень меньше или равен уровню пользователю
                    return True
        return False


    def get_user_data(self,user_id: int):
        self.load()
        for num, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id:
                return num+1, level, un, fn, ln

    def change_permission(self, user_id: int, permission: int):
        for i, (uid, level,un,fn,ln) in enumerate(self.users):
            if uid == user_id:
                if level == permission:
                    return False
                self.users[i][1] = permission
                self.save()
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

        for i in range(target_num):
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=message.message_id - i
                )
            except Exception as e:
                print(f"Не удалось удалить сообщение {message.message_id - i}: {e}")


# ========== GLOBAL INSTANCES ==========
whitelist = WhitelistManager()
newusermanager = NewUserslistManager()
handlermanager = HandlerManager()