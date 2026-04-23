import logging
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import Keyboard, Callback, GroupEventType,KeyboardButtonColor, Text
from VKBot.handlers.config import whitelist, usermanager

labeler = BotLabeler()
logger = logging.getLogger(__name__)

admin_id = 134063156

def get_debug_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("новый_пользователь", payload={"cmd": "new:menu:get"}))
    kb.row()
    kb.add(Callback("админка", payload={"cmd": "admin:menu:get"}))
    kb.row()
    kb.add(Callback("пользователь", payload={"cmd": "user:menu:get"}))
    kb.row()
    kb.add(Callback("добавить админа", payload={"cmd": "debug:add_user"}))
    kb.row()
    kb.add(Callback("выдать права админа", payload={"cmd": "debug:getlvl"}))
    kb.row()
    kb.add(Callback("Добавить заявки", payload={"cmd": "debug:add_random_user"}))
    return kb


def get_commands() -> Keyboard:
    kb = Keyboard(inline=False,one_time=True)  # обычная клавиатура, не инлайн
    kb.add(Text("/start"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("/goadmin"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("/debug"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    return kb

@labeler.message(text=["/commands"])
async def debug_command(message: Message):
    await message.answer("commands\n", keyboard=get_commands().get_json())


@labeler.message(text=["/debug"])
async def debug_command(message: Message):
    await message.answer("debug\n", keyboard=get_debug_keyboard().get_json())

@labeler.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent, blocking=False)
async def handle_callback(event: MessageEvent):
    cmd = event.payload.get("cmd")
    if not (cmd and cmd.startswith("debug:")):
        return None
    if cmd == "debug:add_user":
        target_id = admin_id
        if usermanager.check_user(target_id):
            uid, un, fn, ln = usermanager.all_about_new_user(target_id)
            whitelist.add_user(uid, un, fn, ln)
            usermanager.remove_new_user(target_id)
            await event.edit_message(f"✅ Пользователь одобрен!\nID: {target_id}", keyboard=get_debug_keyboard().get_json())
        else:
            await event.edit_message("⛔ Не получилось добавить пользователя!", keyboard=get_debug_keyboard().get_json())
    elif cmd == "debug:getlvl":
        target_id = admin_id
        whitelist.change_permission(target_id, 2)
        await event.edit_message(f"✅ Пользователю выданы права!\nID: {target_id}", keyboard=get_debug_keyboard().get_json())
    elif cmd == "debug:add_random_user":
        for attempt in range(1, 10):
            if not usermanager.check_user(attempt):
                usermanager.approve_user(attempt, "None", "None", "None")
        await event.edit_message("✅ Заявки созданы!", keyboard=get_debug_keyboard().get_json())
    return True