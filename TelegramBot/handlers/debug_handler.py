from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import whitelist, usermanager
from aiogram.filters import Command
import logging
logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("debug"))
async def debug_new_user(message: types.Message):
    await message.delete()
    await message.answer(
        "debug\n",
        reply_markup=get_debug_keyboard()
    )

def get_debug_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="новый_пользователь", callback_data="new:menu:get")],
        [InlineKeyboardButton(text="админка", callback_data="admin:menu:get")],
        [InlineKeyboardButton(text="пользователь", callback_data="user:menu:get")],
        [InlineKeyboardButton(text="добавить админа", callback_data="debug:add_user")],
        [InlineKeyboardButton(text="выдать права админа", callback_data="debug:getlvl")],
        [InlineKeyboardButton(text="Добавить заявки", callback_data="debug:add_random_user")],
    ])

@router.callback_query(F.data == "debug:add_user")
async def debug_add_user(callback: types.CallbackQuery):
    user_id = 413700636
    if usermanager.check_user(user_id):
        uid, un, fn, ln = usermanager.all_about_new_user(user_id)
        whitelist.add_user(uid, un, fn, ln)
        usermanager.remove_new_user(user_id=user_id)
        await callback.message.edit_text(
            f"✅ Пользователь одобрен!\n"
            f"ID: {user_id}\n",
            reply_markup=get_debug_keyboard()
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            f"⛔Не получилось добавить пользователя!⛔\n",
            reply_markup=get_debug_keyboard()
        )
        await callback.answer()



@router.callback_query(F.data == "debug:getlvl")
async def debug_get_lvl(callback: types.CallbackQuery):
    user_id = 413700636
    whitelist.change_permission(user_id, 2)
    await callback.message.edit_text(
        f"✅ Пользователю выданы права!\n"
        f"ID: {user_id}\n",
        reply_markup=get_debug_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "debug:add_random_user")
async def debug_add_rnd_user(callback: types.CallbackQuery):
    for attempt in range(1, 10):  # 3 попытки
        user_id = attempt
        if not usermanager.check_user(user_id):
            usermanager.approve_user(user_id, "None", "None", "None")
    await callback.message.edit_text(
        f"✅ Заявки созданы!\n",
        reply_markup=get_debug_keyboard()
    )