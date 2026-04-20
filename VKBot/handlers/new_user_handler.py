import logging
from vkbottle.bot import BotLabeler, MessageEvent
from vkbottle import Keyboard, Callback, GroupEventType

from VKBot.handlers import config, keyboards

labeler = BotLabeler()
logger = logging.getLogger(__name__)

def get_new_menu_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("🔍 Мой ID", payload={"cmd": "new:menu:id"}))
    kb.row()
    kb.add(Callback("📨 Запросить | Проверить доступ 🔄", payload={"cmd": "new:menu:get_invite"}))
    kb.row()
    kb.add(Callback("❓ Помощь", payload={"cmd": "new:menu:help"}))
    return kb

@labeler.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent, blocking=False)
async def handle_callback(event: MessageEvent):
    payload = event.payload
    cmd = payload.get("cmd")
    logger.debug(f"new_user_handler получил cmd: {cmd}")

    # Пропускаем события, не начинающиеся с "new:"
    if not (cmd and cmd.startswith("new:")):
        return None

    user_id = event.object.user_id
    peer_id = event.object.peer_id
    conv_msg_id = event.object.conversation_message_id
    event_id = event.object.event_id

    logger.info(f"Обработка new-команды: {cmd} от user_id={user_id}")

    match cmd:
        case "new:menu:get":
            try:
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message="🤖 Добро пожаловать!\nВыберите действие в меню ниже:",
                    keyboard=get_new_menu_keyboard().get_json()
                )
                logger.info("Сообщение успешно отредактировано (new:menu:get)")
            except Exception as e:
                logger.error(f"Ошибка редактирования в new:menu:get: {e}")

        case "new:menu:get_invite":
            try:
                user_info = await event.ctx_api.users.get(user_ids= user_id)
                username = user_info[0].screen_name or ""
                firstname = user_info[0].first_name or ""
                lastname = user_info[0].last_name or ""
            except:
                username = firstname = lastname = ""

            if not config.whitelist.check_user(user_id):
                if config.usermanager.approve_user(user_id, username, firstname, lastname):
                    text = f"ID: {user_id}\nВы запросили доступ. Ожидайте подтверждения."
                    kb = keyboards.get_back_keyboard("new:menu:get")
                else:
                    text = "⛔ Вы уже запрашивали доступ ранее."
                    kb = keyboards.get_back_keyboard("new:menu:get")
            else:
                text = "✅ У вас уже есть доступ!"
                kb = keyboards.keyboardH("Войти", "user:menu:get")

            try:
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message=text,
                    keyboard=kb.get_json()
                )
            except Exception as e:
                logger.error(f"Ошибка редактирования в new:menu:get_invite: {e}")

        case "new:menu:id":
            has_access = config.whitelist.check_user(user_id)
            text = f"📋 Ваш профиль:\n\nID: {user_id}\nДоступ: {'✅ разрешен' if has_access else '❌ запрещен'}"
            kb = keyboards.get_back_keyboard("new:menu:get")
            try:
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message=text,
                    keyboard=kb.get_json()
                )
            except Exception as e:
                logger.error(f"Ошибка редактирования в new:menu:id: {e}")

        case "new:menu:help":
            text = (
                "ℹ️ Помощь:\n\n"
                "• Бот работает по вайтлисту\n"
                "• Только добавленные пользователи имеют доступ\n"
                "• Админ может добавлять новых пользователей\n"
                "• У вас пока нет прав.\n\n"
                "Команды:\n/start - главное меню"
            )
            kb = keyboards.get_back_keyboard("new:menu:get")
            try:
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=conv_msg_id,
                    message=text,
                    keyboard=kb.get_json()
                )
            except Exception as e:
                logger.error(f"Ошибка редактирования в new:menu:help: {e}")

        case _:
            return None