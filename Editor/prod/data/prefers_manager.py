import json
import os

userdata_directory:str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user" ))
def save_config(theme:str=None,language:str=None, filename="prefers.json"):
    error = None
    print("попытка сохранения конфигурации")
    try:
        if theme == None:
            theme,_ = load_config()
        if language == None:
            _,language = load_config()
        save_structure = {
            "theme": theme,
            "language": language,
        }
        with open(userdata_directory+"/"+filename, "w", encoding='utf-8') as file:
            json.dump(save_structure, file, ensure_ascii=False, indent=2)
        return True,error
    except Exception as error:
        return False, error


def load_config(filename: str = "prefers.json"):
    if not os.path.exists(userdata_directory+"/"+filename):
        first_save()

    with open(userdata_directory+"/"+filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    theme = data.get("theme", "")
    language = data.get("language", "")

    return theme,language

def first_save():
    save_config("light","RU")