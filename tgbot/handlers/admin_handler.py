from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager
import handlers.user_handler as uh


router = Router()

############################доделать режим редактирования
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
    ]
    ])

def get_edit_2_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="◀️ Назад 3в меню", callback_data="back_to_admin_menu"),
        InlineKeyboardButton(text="🔧 Редакт3ировать", callback_data="edit_usr_lst"),
        InlineKeyboardButton(text="🔧 Редакт3ировать", callback_data="edit_usr_lst"),
        InlineKeyboardButton(text="🔧 Редакт3ировать", callback_data="edit_usr_lst"),
    ]
    ])

# ========== КОМАНДЫ ==========

@router.callback_query(F.data == "logined_user")
async def logined_user(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    whitelist.load()

    if not whitelist.check_user(user_id):
        await callback.message.answer("⛔ У вас нет доступа к боту\n")
    else:
        if whitelist.check_permission(user_id) == 2:
            await callback.message.answer( #админ
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

    if user_level == 2:  # 2 = Администратор
        if not newusermanager.users:
            user_list = "Список пуст"
            keyboard = get_back_admin_keyboard()
        else:
            user_entries = []
            for num, (uid, un, fn, ln) in enumerate(newusermanager.users, 1):
                user_entries.append(f"• №{num} | ID: {uid} | {un} | {fn} {ln}")

            user_list = "\n".join(user_entries)

            # Создаем кнопки для одобрения пользователей
            buttons = []
            for num, (uid, un, fn, ln) in enumerate(newusermanager.users, 1):
                print(uid)
                if num <= 5:  # Ограничиваем 5 кнопками
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

    await callback.answer()  # ⚠️ ВСЕГДА В КОНЦЕ!

@router.callback_query(F.data.startswith("admin_approve_"))
async def show_user_list(callback: types.CallbackQuery):
    user_id_str = callback.data.replace("admin_approve_", "")
    user_id = int(user_id_str)
    uid,un,fn,ln = newusermanager.all_about_new_user(user_id)
    whitelist.add_user(uid,un,fn,ln)
    newusermanager.remove_new_user(user_id=user_id)
    await callback.message.edit_text(
        f"✅ Пользователь одобрен!\n"
        f"ID: {user_id}\n",
        reply_markup=get_back_admin_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_userlist")
async def show_user_list(callback: types.CallbackQuery):
    if whitelist.users == []:
        user_list_str = "Список пуст"
    else:
        whitelist.save()
        whitelist.load()
        user_list_str = "\n".join([
            f"• №{num+1} | ID: {uid} | Ур.: {whitelist.user_lvl[level][:3] if level < len(whitelist.user_lvl) else 'Неизв.'}. | @{un} | {fn} {ln}"
            for num,(uid, level, un, fn, ln) in enumerate(whitelist.users)
        ])

    await callback.message.edit_text(
    f"📋 Пользователи в вайтлисте:\n\n{user_list_str}\n\n"
    f"Всего: {len(whitelist.users)} пользователей",
    reply_markup=get_edit_keyboard()
    )

    await callback.answer()

@router.callback_query(F.data == "back_to_user_menu")
async def back_to_user_menu(callback: types.CallbackQuery):
    await callback.answer(  # обычный пользователь
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

@router.callback_query(F.data == "edit_usr_lst")
async def edit_usr_lst(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    if not whitelist.check_user(user_id):
        await callback.message.edit_text("⛔ У вас нет доступа к боту")
        return

    await callback.message.edit_text(
    f"Напишите номер пользователя для редактирования\n\n"
    f"Всего: {len(whitelist.users)} пользователей",
    reply_markup=get_edit_2_keyboard()
    )
    await callback.answer()
