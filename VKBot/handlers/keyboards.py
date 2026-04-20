from vkbottle import Keyboard, KeyboardButtonColor, Callback

def user_edit_keyboard(user_id: int) -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("↩️ Назад", payload={"cmd": "admin:menu:get"}))
    kb.add(Callback("Выдать Админа", payload={"cmd": f"edit_{user_id}_adm"}))
    kb.add(Callback("Удалить", payload={"cmd": f"edit_{user_id}_del"}))
    return kb

def keyboardH(text_1="↩️ Назад", callback_1="user:menu:get", text_2="", callback_2="",
              text_3="", callback_3="", text_4="", callback_4="") -> Keyboard:
    kb = Keyboard(inline=True)
    for i, (t, c) in enumerate([(text_1, callback_1), (text_2, callback_2), (text_3, callback_3), (text_4, callback_4)]):
        if t:
            kb.add(Callback(t, payload={"cmd": c}), color=KeyboardButtonColor.PRIMARY if i == 0 else KeyboardButtonColor.SECONDARY)
    return kb

def keyboardV(text_1="↩️ Назад", callback_1="user:menu:get", text_2="", callback_2="",
              text_3="", callback_3="", text_4="", callback_4="") -> Keyboard:
    kb = Keyboard(inline=True)
    for i, (t, c) in enumerate([(text_1, callback_1), (text_2, callback_2), (text_3, callback_3), (text_4, callback_4)]):
        if t:
            if i > 0: kb.row()
            kb.add(Callback(t, payload={"cmd": c}))
    return kb

def keyboard_buttons(buttons: list) -> Keyboard:
    kb = Keyboard(inline=True)
    for i, (t, c) in enumerate(buttons):
        if i > 0: kb.row()
        kb.add(Callback(t, payload={"cmd": c}))
    return kb

def get_back_keyboard(callback="user:menu:get", text="↩️ Назад") -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback(text, payload={"cmd": callback}), color=KeyboardButtonColor.NEGATIVE)
    return kb

def get_back_to_new_menu_keyboard() -> Keyboard:
    kb = Keyboard(inline=True)
    kb.add(Callback("↩️ Назад", payload={"cmd": "new:menu:get"}), color=KeyboardButtonColor.NEGATIVE)
    return kb

def loading(rdy_num:int, nrdy_num:int = 10) -> str:
    return "⬛" * rdy_num + "🔲" * (nrdy_num - rdy_num)