import json
from pathlib import Path
from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()

class AddUserStates(StatesGroup):
    waiting_for_user_id = State()  # Состояние ожидания ID пользователя


class WhitelistManager:
    def __init__(self, file_path="bin/whitelist.json"):
        self.file_path = Path(file_path)
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                self.users = set(json.load(f))
        else:
            self.users = set()

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(list(self.users), f)

    def add_user(self, user_id: int):
        self.users.add(user_id)
        self.save()

    def remove_user(self, user_id: int):
        self.users.discard(user_id)
        self.save()

    def check_user(self, user_id: int) -> bool:
        return user_id in self.users


# Использование
whitelist = WhitelistManager()

ADMIN_ID = 413700636
BOT_ID = 8034081320

# Добавление пользователя (например, через команду админа)

@router.message(Command("add_user"))
async def add_user_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Введите ID пользователя для добавления в вайтлист:")
        await state.set_state(AddUserStates.waiting_for_user_id)
    else:
        await message.answer("❌ У вас нет прав для этой команды")

@router.message(lambda m: m.text in ["🔍 Узнать мой ID",Command("/myid")])
async def get_my_id(message: types.Message):
    user_id = message.from_user.id
    whitelist.load()
    await message.answer(f"Ваш ID: `{user_id}`\n"f"Доступ: {'✅ разрешён' if whitelist.check_user(user_id) else '❌ запрещён'}",
                        parse_mode="Markdown")


@router.message(AddUserStates.waiting_for_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id_text = message.text.strip()

    # Проверяем, что введено число
    if not user_id_text.isdigit():
        await message.answer("❌ Введите число (ID пользователя):")
        return  # Остаемся в том же состоянии

    user_id = int(user_id_text)

    # Добавляем в вайтлист
    whitelist.add_user(user_id)
    await message.answer(f"✅ Пользователь {user_id} добавлен")

    # Сбрасываем состояние
    await state.clear()