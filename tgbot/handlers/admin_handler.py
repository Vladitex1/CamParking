from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager
import handlers.user_handler as uh
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Bot

router = Router()


class Form(StatesGroup):
    waiting_user_id = State()
    waiting_edit_field = State()
    waiting_new_value = State()


# ========== КЛАВИАТУРЫ ==========
def get_admin_main_menu(user_id: int) -> InlineKeyboardMarkup:

    if whitelist.check_permission(user_id) == 2:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu_admin_myid")],
            [InlineKeyboardButton(text="🆕 Одобрить пользователя", callback_data="menu_adduser")],
            [InlineKeyboardButton(text="📋 Список пользователей", callback_data="menu_userlist")],
            [InlineKeyboardButton(text="◀️ Назад к пользовательскому меню", callback_data="back_to_menu")]
        ])


def get_back_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_admin_menu")]
    ])


def get_edit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_admin_menu"),
        InlineKeyboardButton(text="🔧 Редактировать", callback_data="edit_usr_lst"),
    ]])


def approve_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="menu_userlist"),
    ]])


def user_edit_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_admin_menu"),
        InlineKeyboardButton(text="Выдать права администратора", callback_data=f"edit_{user_id}_adm"),
        InlineKeyboardButton(text="Удалить пользователя", callback_data=f"edit_{user_id}_del"),
    ]])


# ========== КОМАНДЫ ==========
@router.callback_query(F.data == "logined_user")
async def logined_user(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    whitelist.load()

    if not whitelist.check_user(user_id):
        await callback.message.answer("⛔ У вас нет доступа к боту\n")
    else:
        if whitelist.check_permission(user_id) == 2:
            await callback.message.answer(
                "🤖 Добро пожаловать!\n"
                "Выберите действие в меню ниже:",
                reply_markup=get_admin_main_menu(user_id))


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "menu_admin_myid")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    level = whitelist.check_permission(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: `{user_id}`\n"
        f"Доступ: {'✅ разрешен' if whitelist.check_user(user_id) else '❌ запрещен'}\n"
        f"Уровень учетной записи: `{whitelist.user_lvl[level]}`\n",
        reply_markup=get_back_admin_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_adduser")
async def add_user_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_level = whitelist.check_permission(user_id)

    if user_level == 2:
        if not newusermanager.users:
            user_list = "Список пуст"
            keyboard = get_back_admin_keyboard()
        else:
            user_entries = []
            for num, (uid, un, fn, ln) in enumerate(newusermanager.users, 1):
                user_entries.append(f"• №{num} | ID: {uid} | {un} | {fn} {ln}")

            user_list = "\n".join(user_entries)

            buttons = []
            for num, (uid, un, fn, ln) in enumerate(newusermanager.users, 1):
                if num <= 5:
                    button_text = f"➕ Одобрить #{num} ({fn})"
                    callback_data = f"admin_approve_{uid}"
                    buttons.append([InlineKeyboardButton(
                        text=button_text,
                        callback_data=callback_data
                    )])

            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons + [
                [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin_menu")]
            ])

        await callback.message.edit_text(
            f"📋 Заявки на доступ ({len(newusermanager.users)}):\n\n{user_list}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "⛔ Только администратор может просматривать заявки",
            reply_markup=get_back_admin_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_user(callback: types.CallbackQuery):
    user_id_str = callback.data.replace("admin_approve_", "")
    user_id = int(user_id_str)
    uid, un, fn, ln = newusermanager.all_about_new_user(user_id)
    whitelist.add_user(uid, un, fn, ln)
    newusermanager.remove_new_user(user_id=user_id)
    await callback.message.edit_text(
        f"✅ Пользователь одобрен!\n"
        f"ID: {user_id}\n",
        reply_markup=get_back_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu_userlist")
async def show_user_list(callback: types.CallbackQuery):
    if not whitelist.users:
        user_list_str = "Список пуст"
    else:
        user_list_str = "\n".join([
            f"• №{num + 1} | ID: {uid} | Ур.: {whitelist.user_lvl[level][:3] if level < len(whitelist.user_lvl) else 'Неизв.'}. | @{un} | {fn} {ln}"
            for num, (uid, level, un, fn, ln) in enumerate(whitelist.users)
        ])

    await callback.message.edit_text(
        f"📋 Пользователи в вайтлисте:\n\n{user_list_str}\n\n"
        f"Всего: {len(whitelist.users)} пользователей",
        reply_markup=get_edit_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_user_menu")
async def back_to_user_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Меню пользователя",
        reply_markup=uh.get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not whitelist.check_user(user_id):
        await callback.message.edit_text("⛔ У вас нет доступа к боту")
        return

    await callback.message.edit_text(
        f"🤖 Добро пожаловать, {callback.from_user.first_name}!\n"
        "Режим администрирования:",
        reply_markup=get_admin_main_menu(user_id)
    )
    await callback.answer()


# ========== РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ ==========
@router.callback_query(F.data == "edit_usr_lst")
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID пользователя для редактирования:")
    await state.set_state(Form.waiting_user_id)
    await callback.answer()


@router.message(Form.waiting_user_id)
async def process_user_id(message: types.Message, state: FSMContext,bot: Bot):
    try:
        input_id = int(message.text)
        await message.delete()
        # Проверяем существование пользователя
        user_exists = False
        user_data = None

        for uid, level, un, fn, ln in whitelist.users:
            if uid == input_id:
                user_exists = True
                user_data = (level, un, fn, ln)
                break

        if not user_exists:
            await message.answer("❌ Пользователь не найден. Попробуйте еще раз:",
                                 reply_markup=get_back_admin_keyboard())
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id - 1  # Предыдущее сообщение
            )
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id - 2  # Предыдущее сообщение
            )
            await state.clear()
            return

        # Показываем информацию о пользователе
        level, un, fn, ln = user_data
        await message.answer(
            f"👤 *Данные пользователя:*\n"
            f"ID: `{input_id}`\n"  # Обратные кавычки делают текст копируемым
            f"Уровень: {whitelist.user_lvl[level] if level < len(whitelist.user_lvl) else 'Неизвестно'}\n"
            f"Username: @{un}\n"
            f"Имя: {fn} {ln}\n\n"
            "Выберите действие:",
            parse_mode="Markdown",
            reply_markup=user_edit_keyboard(input_id)
        )
        # ОЧИЩАЕМ СОСТОЯНИЕ
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id - 1  # Предыдущее сообщение
        )
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id - 2  # Предыдущее сообщение
        )
        await state.clear()

    except ValueError:

        await message.answer("❌ Введите числовой ID пользователя:")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id - 1  # Предыдущее сообщение
        )
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id - 2  # Предыдущее сообщение
        )
        await state.clear()


@router.callback_query(F.data.startswith("edit_"))
async def edit_user_action(callback: types.CallbackQuery):
    try:
        parts = callback.data.split("_")
        user_id = int(parts[1])
        action = parts[2]

        if action == "del":
            status = whitelist.delete_user(user_id,callback.from_user.id)
            if status:
                await callback.message.edit_text(
                    f"✅ Пользователь {user_id} удален",
                    reply_markup=get_back_admin_keyboard()
                )
            else:
                await callback.message.edit_text(
                    f"Удаление не удалось. Вы не можете удалить самого себя.",
                    reply_markup=get_back_admin_keyboard()
                )
        elif action == "adm":
            status = whitelist.change_permission(user_id, 2)
            if status:
                await callback.message.edit_text(
                    f"✅ Пользователю {user_id} выданы права администратора",
                    reply_markup=get_back_admin_keyboard()
                )
            else:
                await callback.message.edit_text(
                    f"❌ У пользователя уже есть эти права",
                    reply_markup=get_back_admin_keyboard()
                )
        else:
            await callback.message.edit_text("❌ Неизвестное действие")
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")

    await callback.answer()


# ========== ВСЕ ОСТАЛЬНЫЕ СООБЩЕНИЯ ==========
@router.message()
async def handle_unknown(message: types.Message):
    await message.delete()


@router.callback_query()
async def handle_unknown_callback(callback: types.CallbackQuery):
    # Игнорируем неизвестные callback
    await callback.answer()