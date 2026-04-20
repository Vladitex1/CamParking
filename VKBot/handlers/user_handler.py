
import logging
import os
import random
from datetime import datetime
from PIL import Image

from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import Keyboard, KeyboardButtonColor, Callback, PhotoMessageUploader, GroupEventType

from VKBot.handlers.config import whitelist
import VKBot.handlers.keyboards as keyboards
from logic import detector, visualizer, camera_control


labeler = BotLabeler()
logger = logging.getLogger(__name__)

user_states = {}
photo_uploader = None

def setup_uploader(api):
    global photo_uploader
    photo_uploader = PhotoMessageUploader(api)

def get_main_user_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("🅿️ Свободные места", payload={"cmd": "parking:get"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Callback("⚙️ Настройки", payload={"cmd": "parking:settings"}), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Callback("❓ Помощь", payload={"cmd": "user:menu:help"}), color=KeyboardButtonColor.SECONDARY)
    kb.add(Callback("🔍 Мой ID", payload={"cmd": "user:menu:id"}), color=KeyboardButtonColor.SECONDARY)
    return kb

def get_settings_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("Проверить статус камеры", payload={"cmd": "parking:settings:check_ip"}))
    kb.row()
    kb.add(Callback("Назначить адрес камеры", payload={"cmd": "parking:settings:set_ip"}))
    kb.row()
    kb.add(Callback("Выбор маски", payload={"cmd": "parking:settings:select_mask"}))
    kb.row()
    kb.add(Callback("Выбор конфигурации распознавания", payload={"cmd": "parking:settings:select_config"}))
    kb.row()
    kb.add(Callback("Название на изображении", payload={"cmd": "parking:settings:select_letters"}))
    kb.row()
    kb.add(Callback("Назад", payload={"cmd": "user:menu:get"}), color=KeyboardButtonColor.NEGATIVE)
    return kb

def get_select_letters_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("Включить", payload={"cmd": "parking:settings:set_letters", "letters": "1"}))
    kb.row()
    kb.add(Callback("Выключить", payload={"cmd": "parking:settings:set_letters", "letters": "0"}))
    kb.row()
    kb.add(Callback("Назад", payload={"cmd": "parking:settings"}), color=KeyboardButtonColor.NEGATIVE)
    return kb

def get_select_mask_keyboard() -> Keyboard:
    path: str = "../save"
    result = os.listdir(path=path)
    kb = Keyboard(inline=True)
    # Добавляем все маски в одну строку (если их немного)
    for i,mask_name in enumerate(result):
        kb.add(Callback(mask_name, payload={"cmd": "parking:settings:set_mask", "mask": f"{mask_name}"}))
        if (i + 1) % 3 == 0 and i < len(result) - 1:
            kb.row()
        if i == 7:
            break
    # Добавляем кнопку "Загрузить маску" на новой строке
    kb.row()
    kb.add(Callback("Загрузить маску", payload={"cmd": "parking:settings:load_mask"}))

    # Добавляем кнопку "Назад" на новой строке
    kb.row()
    kb.add(Callback("Назад", payload={"cmd": "parking:settings"}), color=KeyboardButtonColor.NEGATIVE)

    return kb

def get_select_config_keyboard() -> Keyboard:
    path: str = "../model/config"
    result = os.listdir(path=path)
    print(result)

    kb = Keyboard(inline=True)

    # Размещаем по 2 кнопки в строке
    for i, config_name in enumerate(result):
        kb.add(Callback(config_name, payload={"cmd": "parking:settings:set_config", "config": f"{config_name}"}))
        kb.row()
        # После каждых 2 кнопок добавляем новую строку (кроме последней)
        #if (i + 1) % 3 == 0 and i < len(result) - 1:
        #    kb.row()
        if i == 7:
            break

    # Добавляем кнопку "Назад" на новой строке
    kb.row()
    kb.add(Callback("Назад", payload={"cmd": "parking:settings"}), color=KeyboardButtonColor.NEGATIVE)

    return kb


async def show_settings_menu(event: MessageEvent, user_id: int,check_ip:bool=False):
    """Показывает меню настроек с актуальными данными"""
    if whitelist.valid_user_permissions(user_id, 1):
        mask = whitelist.get_settings('mask', user_id)
        ip = whitelist.get_settings('ip', user_id)
        cameratest = "🟢" if check_ip else "🔴"
        letters = whitelist.get_settings('letters', user_id)
        #user_mask = whitelist.get_settings('user_mask_slot_1', user_id)
        config = whitelist.get_settings('config', user_id)
        text = (f"🔧 Основные настройки 🔧"
                f"\n"
                f"  - 🌐 Адрес камеры: {ip}\n"
                f"  - 📸 Статус: {cameratest}\n"
                f"  - 🤿 Выбранная маска: {mask}\n"
                f"  - ⚙️ Выбранная конфигурация: {config}"
                f"\n\n"
                f"✨ Внешний вид ✨"
                f"\n"
                f"  - 🔤 Включение имен на местах: {'Включено' if letters == '1' else 'Выключено'}\n"
                )
        await event.edit_message(text, keyboard=get_settings_keyboard().get_json())
    else:
        await event.edit_message(
            "⛔ У вас нет доступа к этому меню",
            keyboard=keyboards.get_back_to_new_menu_keyboard().get_json()
        )

@labeler.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent, blocking=False)
async def handle_callback(event: MessageEvent):
    user_id = event.object.user_id
    if whitelist.valid_user_permissions(user_id, 1):
        payload = event.payload
        cmd = payload.get("cmd")
        if not (cmd and (cmd.startswith("user:") or cmd.startswith("parking:"))):
            return None

        peer_id = event.object.peer_id
        conv_msg_id = event.object.conversation_message_id

        if cmd == "user:menu:get":
            await event.edit_message("Выберите действие в меню ниже:", keyboard=get_main_user_keyboard().get_json())


        elif cmd == "parking:get":
            user_states[user_id] = {"state": "waiting_camera"}
            await process_camera_request(event, user_id, peer_id, conv_msg_id)

        elif cmd == "user:menu:help":
            text = (f"ℹ️ Помощь:\n\n"
                    f"Перед началом работы:\n\n"
                    f"Для получения доступа к камере необходимо: \n"
                    f"  - Добавить адрес камеры \n"
                    f" (доступно в приложении, в меню 'подключение')\n"
                    f"  - Загруить и/или выбрать сохраненную маску\n"
                    f"  - Выбрать конфигурацию Yolo\n\n"
                    f"Также для удобства есть возможность включить имена на изображении (опционально)\n\n"
                    f"Связь с разработчиком:\n "
                    f"  - Telegram - @gsoalnfeea\n"
                    f"  - VK - @vladitex1")
            await event.edit_message(
                text,
                keyboard=keyboards.get_back_keyboard("user:menu:get").get_json()
            )

        elif cmd == "user:menu:id":
            level = whitelist.check_permission(user_id)
            user_data = whitelist.get_user_data(user_id)
            text = (f"📋 Ваш профиль:\n{user_data[2]} | {user_data[3]} | {user_data[4]}\nID: {user_id}\n"
                    f"Доступ: {'разрешен ✅' if whitelist.check_user(user_id) else 'запрещен ❌'}\n"
                    f"Уровень: {whitelist.user_lvl[level]} | {whitelist.user_lvl_icon[level]}\n")
            kb = Keyboard(inline=True)
            kb.add(Callback("Назад", payload={"cmd": "user:menu:get"}))
            if level == 2:
                kb.row()
                kb.add(Callback("Администрирование", payload={"cmd": "admin:menu:get"}))
            await event.edit_message(text, keyboard=kb.get_json())

        elif cmd == "parking:settings":
            await show_settings_menu(event, user_id)

        # Активация спец клавиатур
        elif cmd == "parking:settings:select_mask":
            mask = whitelist.get_settings('mask', user_id)
            text = (f"🔧 Настройки 🔧\n\n"
                    f"🤿 Выбранная маска: {mask}\n")
            await event.edit_message(
                text,
                keyboard=get_select_mask_keyboard().get_json()
            )

        elif cmd == "parking:settings:select_config":
            config = whitelist.get_settings('config', user_id)
            text = (f"🔧 Настройки распознавания 🔧\n\n"
                    f"🤿 Выбранный конфиг распознавания: {config} \n")
            await event.edit_message(
                text,
                keyboard=get_select_config_keyboard().get_json()
            )

        elif cmd == "parking:settings:select_letters":
            letters = whitelist.get_settings('letters', user_id)
            text = (f"🔧  Название парковочных мест на фото 🔧\n\n"
                    f"🤿  Текущее состояние: {'Включено' if letters == '1' else 'Выключено'}\n")
            await event.edit_message(
                text,
                keyboard=get_select_letters_keyboard().get_json()
            )

        elif cmd == "parking:settings:check_ip":
            if whitelist.get_settings('ip',user_id) == "0" or whitelist.get_settings('ip',user_id) == "None":
                await show_settings_menu(event, user_id, check_ip=False)
            else:
                await show_settings_menu(event, user_id,check_ip=await camera_control.camera_test(whitelist.get_settings('ip',user_id)))

        # Применение настроек
        elif cmd == "parking:settings:set_ip":
            # Устанавливаем состояние ожидания ввода IP
            user_states[user_id] = {"state": "waiting_for_ip"}

            # Создаем клавиатуру с кнопкой "Назад"
            kb = Keyboard(inline=True)
            kb.add(Callback("◀️ Назад", payload={"cmd": "parking:settings"}), color=KeyboardButtonColor.NEGATIVE)

            current_ip = whitelist.get_settings('ip', user_id)
            await event.edit_message(
                f"📷 Настройка IP камеры\n\n"
                f"Текущий IP: {current_ip if current_ip else 'не задан'}\n\n"
                f"Введите новый IP адрес камеры в формате:\n"
                f"rtsp://логин:пароль@ip:порт/путь\n\n"
                f"Пример: rtsp://admin:12345@192.168.1.100:554/stream1\n\n"
                f"Или отправьте '0' для использования тестового изображения",
                keyboard=kb.get_json()
            )

        elif cmd == "parking:settings:set_mask":
            mask_name = payload.get("mask")
            whitelist.set_settings(setting_name="mask", user_id=user_id, value=mask_name)
            await show_settings_menu(event, user_id)

        elif cmd == "parking:settings:set_letters":
            letters_name = payload.get("letters")
            whitelist.set_settings(setting_name="letters", user_id=user_id, value=letters_name)
            await show_settings_menu(event, user_id)

        elif cmd == "parking:settings:set_config":
            config_name = payload.get("config")
            whitelist.set_settings(setting_name="config", user_id=user_id, value=config_name)
            await show_settings_menu(event, user_id)

        elif cmd == "parking:settings:load_mask":
            user_states[user_id] = {"state": "load_file"}
            await event.edit_message(
                "Отправьте файл маски (.mask) в чат",
                keyboard=keyboards.get_back_keyboard("parking:settings").get_json()
            )

        elif cmd == "parking:back":
            try:
                await event.ctx_api.messages.delete(peer_id=peer_id,
                                                    conversation_message_ids=[conv_msg_id - 1, conv_msg_id],
                                                    delete_for_all=True)
            except:
                pass

        else:
            return
    else:
        await event.edit_message(
            "⛔ У вас нет доступа к этому меню",
            keyboard=keyboards.get_back_to_new_menu_keyboard().get_json()
        )

@labeler.message(blocking=False)
async def handle_state_message(message: Message):
    user_id = message.from_id
    state_info = user_states.get(user_id)

    if not state_info:
        return False

    # Обработка загрузки файла маски
    if state_info["state"] == "load_file":
        if message.attachments:
            await message.answer("Файл маски получен, но загрузка пока не реализована для VK.")
        else:
            await message.answer("Ожидался файл маски (.mask). Попробуйте снова.")
        del user_states[user_id]
        return True

    # Обработка ввода IP адреса
    elif state_info["state"] == "waiting_for_ip":
        ip_address = message.text.strip()

        # Проверка на отмену (если пользователь отправил "назад" или "/cancel")
        if ip_address.lower() in ["назад", "/cancel", "/back"]:
            # Возвращаем в меню настроек через callback
            del user_states[user_id]
            # Создаем фейковое событие для возврата
            await message.answer(
                "Возврат в меню настроек",
                keyboard=keyboards.get_back_keyboard("parking:settings").get_json()
            )
            return True

        # Сохраняем IP (даже если '0' - это тестовый режим)
        whitelist.set_settings(setting_name="ip", user_id=user_id, value=ip_address)

        # Очищаем состояние
        del user_states[user_id]

        # Показываем сообщение об успехе
        if ip_address == "0":
            await message.answer(
                "✅ Установлен тестовый режим (будут использоваться локальные изображения)\n"
                "Нажмите 'Назад' для возврата в меню",
                keyboard=keyboards.get_back_keyboard("parking:settings").get_json()
            )
        else:
            await message.answer(
                f"✅ IP адрес камеры сохранен:\n{ip_address}\n"
                f"Нажмите 'Назад' для возврата в меню",
                keyboard=keyboards.get_back_keyboard("parking:settings").get_json()
            )
        return True

    return False

# ========== ИСПРАВЛЕННЫЕ ФУНКЦИИ ==========
async def process_camera_request(event: MessageEvent, user_id: int, peer_id: int, conv_msg_id: int):
    if whitelist.valid_user_permissions(user_id, 1):
    # Удаляем исходное сообщение с кнопкой (если есть)
        if conv_msg_id:
            try:
                await event.ctx_api.messages.delete(peer_id=peer_id, conversation_message_ids=[conv_msg_id], delete_for_all=True)
            except Exception as e:
                logger.debug(f"Не удалось удалить исходное сообщение: {e}")

        # Отправляем сообщение-загрузку, используя peer_ids для получения conversation_message_id
        try:
            send_response = await event.ctx_api.messages.send(peer_ids=str(peer_id), message="Загрузка: \n" + keyboards.loading(0), random_id=random.getrandbits(31))
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения загрузки: {e}")
            await event.ctx_api.messages.send(
                peer_id=peer_id,
                message="❌ Техническая ошибка. Попробуйте позже.",
                random_id=0,
                keyboard=keyboards.get_back_keyboard("parking:back").get_json()
            )
            return

        # Извлекаем conversation_message_id из ответа
        loading_cmid = None
        if isinstance(send_response, list) and len(send_response) > 0:
            msg_data = send_response[0]
            try:
                loading_cmid = msg_data.conversation_message_id
                logger.debug(f"Отправлено сообщение загрузки: cmid={loading_cmid}")
            except AttributeError:
                logger.error(f"Объект не имеет атрибута conversation_message_id: {msg_data}")
        else:
            logger.error(f"Неожиданный ответ от messages.send: {send_response}")

        if not loading_cmid:
            logger.error("Не удалось получить conversation_message_id")
            await event.ctx_api.messages.send(
                peer_id=peer_id,
                message="❌ Техническая ошибка. Попробуйте позже.",
                random_id=0,
                keyboard=keyboards.get_back_keyboard("parking:back").get_json()
            )
            return

        try:
            INPUT_DIR: str = "../img/results/"
            mask = whitelist.get_settings('mask', user_id)
            config = whitelist.get_settings('config', user_id)
            ip = whitelist.get_settings('ip',user_id)
            names = True if whitelist.get_settings('letters',user_id) == '1' else False
            await edit_loading(event, loading_cmid, peer_id, 1)

            if ip == '0':
                input_image = "../img/camphoto/camera_photo_2026-04-10_21.jpg"
            else:
                input_image = await camera_control.get_img_PyAV(camera_path=ip,out_data_type="data")
                if input_image == 0:
                    raise Exception("Ошибка подключения к камере")
                await edit_loading(event, loading_cmid, peer_id, 3)

            checked_image_data = detector.check_auto(mask=mask, image=input_image, config_name=config)
            if type(checked_image_data) == int:
                print(checked_image_data)
                raise Exception("Ошибка распознавания")
            await edit_loading(event, loading_cmid, peer_id, 6)

            visualized_image = visualizer.detect(image=input_image, mask=mask, occupied_data=checked_image_data, draw_name=names)
            if visualized_image == 0:
                print("Ошибка модификации изображения")
                raise Exception("Ошибка модификации изображения")
            await edit_loading(event, loading_cmid, peer_id, 9)


            free = checked_image_data[1]
            occupied = checked_image_data[0]

            print(checked_image_data[1])
            print(free[1])
            print(occupied[1])


            free_text = "\n".join([f"🟢 {num+1} | {name}" for num,name in free])
            occupied_text = "\n".join([f"🔴 {num+1} | {name}" for num,name in occupied])
            text = (f"{datetime.today().strftime('📅 %Y-%m-%d 🕔 %H:%M:%S')}\n"
                    f"ℹ️ Информация по парковочным местам:\n\n" #\nИспользованная маска: {mask}
                    f"{free_text}\n\n{occupied_text}\n\nСвободных мест: {len(free)} из {len(free)+len(occupied)}")


            img = Image.open(visualized_image[1])
            compressed_path = INPUT_DIR + "temp_compressed.jpg"

            img.save(compressed_path, 'JPEG', quality=60, optimize=True)
            photo_path = compressed_path


            attachment = await photo_uploader.upload(file_source=photo_path, peer_id=peer_id)
            await edit_loading(event, loading_cmid, peer_id, 10)

            # Удаляем сообщение загрузки
            try:
                await event.ctx_api.messages.delete(peer_id=peer_id, conversation_message_ids=[loading_cmid], delete_for_all=True)
            except Exception as e:
                logger.debug(f"Не удалось удалить сообщение загрузки: {e}")

            # Отправляем финальное сообщение
            await event.ctx_api.messages.send(
                peer_id=peer_id,
                message=text,
                attachment=attachment,
                random_id=0,
                keyboard=keyboards.get_back_keyboard("parking:back").get_json()
            )

            try:
                os.remove(compressed_path)
            except:
                pass

        except Exception as e:
            logger.error(f"Ошибка в process_camera_request: {e}")
            try:
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=loading_cmid,
                    message="❌ Произошла ошибка. Попробуйте позже.",
                    keyboard=keyboards.get_back_keyboard("parking:back").get_json()
                )
            except Exception as edit_err:
                logger.error(f"Не удалось отредактировать сообщение об ошибке: {edit_err}")
                await event.ctx_api.messages.send(
                    peer_id=peer_id,
                    message="❌ Произошла ошибка. Попробуйте позже.",
                    random_id=0,
                    keyboard=keyboards.get_back_keyboard("parking:back").get_json()
                )
    else:
        await event.edit_message(
            "⛔ У вас нет доступа к этому меню",
            keyboard=keyboards.get_back_to_new_menu_keyboard().get_json()
        )

async def edit_loading(event: MessageEvent, cmid: int, peer_id: int, step: int):
    """Редактирует сообщение с прогрессом, используя conversation_message_id"""
    try:
        await event.ctx_api.messages.edit(
            peer_id=peer_id,
            conversation_message_id=cmid,
            message="Загрузка: \n" + keyboards.loading(step)
        )
    except Exception as e:
        logger.debug(f"Не удалось отредактировать сообщение {cmid}: {e}")