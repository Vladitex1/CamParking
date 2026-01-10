from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types.error_event import ErrorEvent
from . import keyboards
from .config import whitelist, usermanager
import logging
logger = logging.getLogger(__name__)

class Form(StatesGroup):
    waiting_user_id = State()
    waiting_edit_field = State()
    waiting_new_value = State()

router = Router()


# ========МЕНЮ============
@router.callback_query(F.data == "admin:menu:get")
async def admin_menu(callback: types.CallbackQuery):
    await callback.answer()
    text = "🤖 Добро пожаловать в админ-панель!\n Выберите действие в меню ниже:"

    adminkeyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Одобрить пользователя", callback_data="admin:menu:adduser")],
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin:menu:usrlst")],
        [InlineKeyboardButton(text="◀️ Назад к пользовательскому меню", callback_data="user:menu:get")]
    ])
    user_id = callback.from_user.id

    if not whitelist.check_user(user_id):
        await callback.message.answer(text="⛔ У вас нет доступа к боту\n",
                                      reply_markup=keyboards.keyboardH(callback_1="new:menu:get"), )
        return

    if whitelist.check_permission(user_id) != 2:
        await callback.message.answer(text="⛔ Недостаточно прав", reply_markup=keyboards.keyboardH(callback_1="user:menu:get"))
        return

    for attempt in range(1, 4):  # 3 попытки
        try:
            await asyncio.wait_for(
                callback.message.edit_text(text, reply_markup=adminkeyboard),
                timeout=5.0
            )
            logger.info(f"✅ Успешно с {attempt} попытки")
            return  # выходим из функции

        except asyncio.TimeoutError:
            if attempt == 3:  # последняя попытка
                await callback.message.answer(text, reply_markup=adminkeyboard)
            else:
                await asyncio.sleep(1)  # пауза перед следующей попыткой



# ========== ОБРАБОТЧИКИ КНОПОК ==========

@router.callback_query(F.data == "admin:menu:adduser")
async def add_user_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_level = whitelist.check_permission(user_id)

    userlist = usermanager.users  # список заявок

    if user_level == 2:  # если админ
        userlist_length = len(userlist)

        # ОСНОВНОЕ: создаем базовую клавиатуру с кнопкой "Назад"
        back_keyboard = keyboards.keyboardH(callback_1="admin:menu:get",
                                            text_2="❌ Отклонить всех", callback_2="admin:menu:adduser:del_all")
        if not userlist:
            # Если нет заявок
            await callback.message.edit_text(
                "📋 Список заявок пуст",
                reply_markup=back_keyboard
            )
        else:
            # Формируем текст со списком заявок
            user_entries = []
            approval_buttons = []  # кнопки для одобрения

            for num, (uid, un, fn, ln) in enumerate(userlist, 1):
                username = f"`@{un}`" if un else "без username"
                fullname = f"{fn} {ln}".strip() if fn or ln else "без имени"
                user_entries.append(f"**{num}.** ID: `{uid}` | {username} | {fullname}")

                # Создаем кнопки для одобрения (первые 5 заявок)
                #if num <= 5:
                approve_button_text = f"✅ Одобр."
                approve_callback_data = f"admin_approve_{uid}"
                reject_button_text = f"❌ Отклон."
                reject_callback_data = f"admin_reject_{uid}"
                approval_buttons.append([
                    InlineKeyboardButton(text=f"{num}-{un}",url=f"https://t.me/{un}"),
                    InlineKeyboardButton(text=reject_button_text, callback_data=reject_callback_data),
                    InlineKeyboardButton(text=approve_button_text, callback_data=approve_callback_data)
                ])

            user_list = "\n".join(user_entries)

            # Объединяем кнопки: сначала кнопки одобрения, потом "Назад"
            all_buttons = approval_buttons + back_keyboard.inline_keyboard

            await callback.message.edit_text(
                f"📋 Заявки на доступ ({userlist_length}):\n\n{user_list}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=all_buttons),
                parse_mode="Markdown"
            )
    else:
        await callback.message.edit_text(
            "⛔ Только администратор может просматривать заявки",
            reply_markup=keyboards.keyboardH(callback_1="user:menu:get")
        )

    await callback.answer()

@router.callback_query(F.data == "admin:menu:adduser:next_page")
async def add_user_menu_next_page(callback: types.CallbackQuery):
    pass
@router.callback_query(F.data == "admin:menu:adduser:prev_page")
async def add_user_menu_prev_page(callback: types.CallbackQuery):
    pass

@router.callback_query(F.data == "admin:menu:adduser:del_all")
async def add_user_menu_del_all(callback: types.CallbackQuery):
    usermanager.del_all()
    await callback.message.edit_text("Все заявки были очищены",
                                     reply_markup=keyboards.keyboardH(callback_1="admin:menu:adduser"))




@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_user(callback: types.CallbackQuery):
    user_id_str = callback.data.replace("admin_approve_", "")
    user_id = int(user_id_str)
    uid, un, fn, ln = usermanager.all_about_new_user(user_id)
    whitelist.add_user(uid, un, fn, ln)
    usermanager.remove_new_user(user_id=user_id)
    await callback.message.edit_text(
        f"✅ Пользователь одобрен!\n"
        f"ID: {user_id}\n",
        reply_markup=keyboards.keyboardH(callback_1="admin:menu:adduser"),
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_reject_"))
async def approve_user(callback: types.CallbackQuery):
    user_id_str = callback.data.replace("admin_reject_", "")
    user_id = int(user_id_str)
    usermanager.remove_new_user(user_id=user_id)
    await callback.message.edit_text(
        f"✅ Заявка удалена!\n"
        f"ID: {user_id}\n",
        reply_markup=keyboards.keyboardH(callback_1="admin:menu:adduser"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:menu:usrlst")
async def show_user_list(callback: types.CallbackQuery):
    # ОДИН раз получаем список и сохраняем в переменную
    users = whitelist.get_user_list()  # ← ТОЛЬКО ОДИН РАЗ!
    user_list_str = ""
    if not users:
        user_list_str = "Список пуст"
        total_users = 0
    else:
        for num, (uid, level, un, fn, ln) in enumerate(users):
            text = f"\n• №{num + 1} | `{uid}` | {whitelist.user_lvl_icon[level][:3]} | @{un} | {fn} {ln}"
            user_list_str += text
        total_users = len(users)  # ← сохраняем длину

    await callback.message.edit_text(
        f"📋 Пользователи в вайтлисте:\n{user_list_str}\n\n"
        f"Всего: {total_users} пользователей",  # ← используем сохраненную длину
        reply_markup=keyboards.keyboardH(callback_1="admin:menu:get", text_2="🔧 Редактировать", callback_2="admin:menu:eul"),
        parse_mode="Markdown"
    )
    await callback.answer()



# В каждую функцию добавьте:



# ========== РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ ==========
@router.callback_query(F.data == "admin:menu:eul")
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID пользователя для редактирования:")
    await state.set_state(Form.waiting_user_id)
    await callback.answer()


@router.message(Form.waiting_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    try:
        input_id = int(message.text)

        # Проверяем что вернул get_user_data()
        user_data = whitelist.get_user_data(input_id)
        print(f"DEBUG: get_user_data вернул: {user_data}")  # ← добавь эту строку!

        if not user_data:
            await message.answer("❌ Пользователь не найден.",
                                 reply_markup=keyboards.keyboardH(callback_1="admin:menu:get"))
            await state.clear()
            return

        # user_data должен быть кортежом: (user_id, level, username, firstname, lastname)
        user_id, level, un, fn, ln = user_data  # ← распаковываем
        await message.answer(
            f"👤 *Данные пользователя:*\n"
            f"ID: `{input_id}`\n"
            f"Уровень: {whitelist.user_lvl[level] if level < len(whitelist.user_lvl) else 'Неизвестно'}\n"
            f"Username: @{un}\n"
            f"Имя: {fn} {ln}\n\n"
            "Выберите действие:",
            parse_mode="Markdown",
            reply_markup=keyboards.user_edit_keyboard(input_id)
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите числовой ID пользователя:")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
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
                    reply_markup=keyboards.keyboardH(callback_1="admin:menu:get"),
                )
            else:
                await callback.message.edit_text(
                    f"Удаление не удалось. Вы не можете удалить самого себя.",
                    reply_markup=keyboards.keyboardH(callback_1="admin:menu:get"),
                )
        elif action == "adm":
            status = whitelist.change_permission(user_id, 2)
            if status:
                await callback.message.edit_text(
                    f"✅ Пользователю {user_id} выданы права администратора",
                    reply_markup=keyboards.keyboardH(callback_1="admin:menu:get"),
                )
            else:
                await callback.message.edit_text(
                    f"❌ У пользователя уже есть эти права",
                    reply_markup=keyboards.keyboardH(callback_1="admin:menu:get"),
                )
        else:
            await callback.message.edit_text("❌ Неизвестное действие")
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")

    await callback.answer()


# ========== ВСЕ ОСТАЛЬНЫЕ СООБЩЕНИЯ ==========
#@router.message()
#async def handle_unknown(message: types.Message):
    #await message.delete()


#@router.callback_query()
#async def handle_unknown_callback(callback: types.CallbackQuery):
    # Игнорируем неизвестные callback
    #await callback.answer()


@router.error()
async def global_error_handler(event: ErrorEvent):
    # Логируем ошибку
    if event.update:
        try:
            if event.update.callback_query:
                logger.error(f"⚠️ Произошла ошибка.,{type(event.exception).__name__}:{event.exception}")
            elif event.update.message:
                logger.error(f"⚠️ Произошла ошибка.,{type(event.exception).__name__}:{event.exception}")
        except:
            pass