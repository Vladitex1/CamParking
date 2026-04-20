import logging
from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import Keyboard, Callback, KeyboardButtonColor, GroupEventType
from vkbottle.tools import OpenLinkEvent

from VKBot.handlers.config import whitelist, usermanager
import VKBot.handlers.keyboards as keyboards
# Импортируем правило напрямую для удобства

labeler = BotLabeler()
logger = logging.getLogger(__name__)
admin_states = {}


def get_admin_menu_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("🆕 Одобрить пользователя", payload={"cmd": "admin:menu:adduser"}))
    kb.row()
    kb.add(Callback("📋 Список пользователей", payload={"cmd": "admin:menu:usrlst"}))
    kb.row()
    kb.add(Callback("◀️ Назад к меню", payload={"cmd": "user:menu:get"}),
           color=KeyboardButtonColor.NEGATIVE)
    return kb


@labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    dataclass=MessageEvent,
    blocking=False,
)
async def handle_admin_callbacks(event: MessageEvent):
    user_id = event.object.user_id
    if whitelist.valid_user_permissions(user_id, 2):
        payload = event.payload
        cmd = payload.get("cmd")

        # Проверяем префиксы вручную, так как vkbottle AND-ит правила в декораторе
        if not any(cmd.startswith(p) for p in ["admin:", "edit_", "profile_"]):
            return None


        peer_id = event.object.peer_id
        event_id = event.object.event_id
        conv_msg_id = event.object.conversation_message_id

        match cmd:
            case "admin:menu:get":
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message="🤖 Админ-панель:",
                    keyboard=get_admin_menu_keyboard().get_json()
                )

            case "admin:menu:adduser":
                userlist = usermanager.users
                if not userlist:
                    kb = Keyboard(inline=True)
                    kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:get"}))
                    await event.ctx_api.messages.edit(
                        peer_id=peer_id,
                        conversation_message_id=conv_msg_id,
                        message="Заявок на доступ нет",
                        keyboard=kb.get_json()
                    )
                    return

                admin_states[user_id] = {"state": "waiting_request_id"}
                entries = [f"{i}. ID: {uid} | @{un} | {fn} {ln}" for i, (uid, un, fn, ln) in enumerate(userlist, 1)]
                text = (
                    f"📋 Заявки на доступ ({len(userlist)}):\n\n"
                    + "\n".join(entries)
                    + "\n\nВведите ID пользователя сообщением для одобрения."
                )
                kb = Keyboard(inline=True)
                kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:get"}))
                kb.add(
                    Callback("❌ Отклонить всех", payload={"cmd": "admin:menu:adduser:del_all"}),
                    color=KeyboardButtonColor.NEGATIVE
                )
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message=text,
                    keyboard=kb.get_json()
                )

            case "admin:menu:usrlst":
                users = whitelist.get_user_list()
                if not users:
                    text = "Список пуст"
                else:
                    lines = [
                        f"{i}. {whitelist.user_lvl_icon[level] if level < len(whitelist.user_lvl_icon) else '👤'} "
                        f"ID: {uid} | @{un} | {fn} {ln}"
                        for i, (uid, level, un, fn, ln) in enumerate(users, 1)
                    ]
                    text = "\n".join(lines)
                kb = Keyboard(inline=True)
                kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:get"}))
                kb.add(Callback("🔧 Редактировать", payload={"cmd": "admin:menu:eul"}))
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message=f"📋 Пользователи в вайтлисте:\n\n{text}",
                    keyboard=kb.get_json()
                )

            case "admin:menu:adduser:del_all":
                usermanager.del_all()
                kb = Keyboard(inline=True)
                kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:adduser"}))
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message="Все заявки были очищены",
                    keyboard=kb.get_json()
                )
                await event.show_snackbar("Заявки очищены")

            case "admin:menu:eul":
                admin_states[user_id] = {"state": "waiting_user_id"}
                kb = Keyboard(inline=True)
                kb.add(Callback("↩️ Отмена", payload={"cmd": "admin:menu:get"}))
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message="Введите ID пользователя для редактирования:",
                    keyboard=kb.get_json()
                )

            case _:
                if cmd.startswith("admin_approve_"):
                    target_id = int(cmd.replace("admin_approve_", ""))
                    user_info = usermanager.all_about_new_user(target_id)
                    if user_info:
                        whitelist.add_user(*user_info)
                        usermanager.remove_new_user(target_id)
                        await event.show_snackbar("Пользователь одобрен!")
                        await handle_admin_callbacks(event)
                elif cmd.startswith("admin_reject_"):
                    target_id = int(cmd.replace("admin_reject_", ""))
                    usermanager.remove_new_user(target_id)
                    await event.show_snackbar("Заявка отклонена")
                    await handle_admin_callbacks(event)
                elif cmd.startswith("edit_"):
                    parts = cmd.split("_")
                    target_id = int(parts[1])
                    action = parts[2]
                    if action == "del":
                        success = whitelist.delete_user(target_id, user_id)
                        text = f"✅ Пользователь {target_id} удалён" if success else "❌ Не удалось удалить (нельзя удалить себя)"
                    elif action == "adm":
                        success = whitelist.change_permission(target_id, 2)
                        text = f"✅ Пользователю {target_id} выданы права администратора" if success else "❌ Не удалось изменить права"
                    else:
                        text = "❌ Неизвестное действие"
                    kb = Keyboard(inline=True)
                    kb.add(Callback("↩️ В админ-меню", payload={"cmd": "admin:menu:get"}))
                    await event.ctx_api.messages.edit(
                        peer_id=peer_id,
                        conversation_message_id=conv_msg_id,
                        message=text,
                        keyboard=kb.get_json()
                    )
                elif cmd.startswith("profile_"):
                    uid = cmd.replace("profile_", "")
                    await event.ctx_api.messages.send_message_event_answer(
                        event_id=event_id,
                        user_id=user_id,
                        peer_id=peer_id,
                        event_data=OpenLinkEvent(link=f"https://vk.com/id{uid}").json()
                    )
                else:
                    return None

    else:
        await event.edit_message(
            "⛔ У вас нет доступа к этому меню",
            keyboard=keyboards.get_back_to_new_menu_keyboard().get_json()
        )


@labeler.message(blocking=False)
async def handle_admin_state_message(message: Message):
    user_id = message.from_id
    if user_id not in admin_states:
        return False

    state = admin_states[user_id].get("state")
    if state not in {"waiting_user_id", "waiting_request_id"}:
        return False

    try:
        input_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите числовой ID пользователя.")
        return

    if state == "waiting_request_id":
        request_user = usermanager.all_about_new_user(input_id)
        if not request_user:
            await message.answer(
                "❌ Заявка с таким ID не найдена. Попробуйте снова или нажмите 'Назад'."
            )
            return
        whitelist.add_user(*request_user)
        usermanager.remove_new_user(input_id)
        await message.answer(
            f"✅ Пользователь {input_id} одобрен.",
            keyboard=keyboards.get_back_keyboard("admin:menu:get", "↩️ В админ-меню").get_json()
        )
        del admin_states[user_id]
        return

    user_data = whitelist.get_user_data(input_id)
    if not user_data:
        await message.answer("❌ Пользователь не найден.",
                             keyboard=keyboards.get_back_keyboard("admin:menu:get").get_json())
        del admin_states[user_id]
        return
    uid, level, un, fn, ln = user_data
    text = f"👤 Данные пользователя:\nID: {uid}\nУровень: {whitelist.user_lvl[level]}\nUsername: @{un}\nИмя: {fn} {ln}\n\nВыберите действие:"
    kb = Keyboard(inline=True)
    kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:get"}))
    kb.add(Callback("Выдать Админа", payload={"cmd": f"edit_{uid}_adm"}))
    kb.add(Callback("Удалить", payload={"cmd": f"edit_{uid}_del"}))
    await message.answer(text, keyboard=kb.get_json())
    del admin_states[user_id]