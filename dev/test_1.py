import asyncio
import logic.camera_control as camera


async def asd():
    data = await camera.get_img_PyAV(out_data_type="data")
    return data

# Запускаем асинхронную функцию и печатаем результат
result = asyncio.run(asd())
print(type(result))
print(result)  # если нужно вывести содержимое


def beckup():
    async def process_camera_request(event: MessageEvent, user_id: int, peer_id: int, conv_msg_id: int):
        if event:
            try:
                await event.ctx_api.messages.delete(peer_id=peer_id, conversation_message_ids=[conv_msg_id],
                                                    delete_for_all=True)
            except:
                pass
        wait_msg = await event.ctx_api.messages.send(
            peer_id=peer_id,
            message="Загрузка: \n" + keyboards.loading(0),
            random_id=0
        )
        wait_msg_id = wait_msg
        error = None
        try:
            INPUT_DIR = "../img/results/"
            mask = whitelist.get_settings('mask', user_id)
            config = whitelist.get_settings('config', user_id)
            await edit_loading(wait_msg_id, peer_id, 1)
            try:
                image_path = await camera.get_img_PyAV()
                if image_path == 0:
                    return 0
                else:
                    await edit_loading(wait_msg_id, peer_id, 2)
                    try:
                        occupied, free = detector.check_auto(mask=mask, processed_image=image_path, config_name=config)
                        await edit_loading(wait_msg_id, peer_id, 5)
                        try:
                            image, filename = visualizer.detect(image_path=image_path, mask=mask,
                                                                occupied_data=[occupied, free], draw_name=False)
                            await edit_loading(wait_msg_id, peer_id, 8)
                        except Exception as e:
                            error = "Ошибка генерации изображения"
                    except Exception as e:
                        error = "Ошибка в распознавании"
            except Exception as e:
                if error == None:
                    error = "Ошибка в подключении к камере"
                logger.error(f"{error} {e}")
                await event.ctx_api.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=wait_msg_id,
                    message=f"❌ Произошла ошибка. Попробуйте позже. {error}",
                    keyboard=keyboards.get_back_keyboard("parking:back").get_json()
                )

            free_text = "\n".join([f"🟢 {s}" for s in free])
            occupied_text = "\n".join([f"🔴 {s}" for s in occupied])
            text = (f"{datetime.today().strftime('📅 %Y-%m-%d 🕔 %H:%M:%S')}\n"
                    f"ℹ️ Информация по парковочным местам:\nИспользованная маска: {mask}\n"
                    f"{free_text}\n{occupied_text}\nСвободных мест: {len(free)} из {len(free) + len(occupied)}")

            img = Image.open(filename)
            compressed_path = INPUT_DIR + "temp_compressed.jpg"
            img.save(compressed_path, 'JPEG', quality=60, optimize=True)
            photo_path = compressed_path

            await edit_loading(wait_msg_id, peer_id, 10)
            attachment = await photo_uploader.upload(file_source=photo_path, peer_id=peer_id)

            await event.ctx_api.messages.send(
                peer_id=peer_id,
                message=text,
                attachment=attachment,
                random_id=0,
                keyboard=keyboards.get_back_keyboard("parking:back").get_json()
            )
            try:
                await event.ctx_api.messages.delete(peer_id=peer_id, conversation_message_ids=[wait_msg_id],
                                                    delete_for_all=True)
            except:
                pass
            try:
                os.remove(compressed_path)
            except:
                pass
        except Exception as e:
            logger.error(f"Ошибка в process_camera_request: {e}")
            await event.ctx_api.messages.edit(
                peer_id=peer_id,
                conversation_message_id=wait_msg_id,
                message="❌ Произошла ошибка. Попробуйте позже.",
                keyboard=keyboards.get_back_keyboard("parking:back").get_json()
            )
