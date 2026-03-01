import json
import os

userdata_directory:str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user" ))
def save_config(theme, filename="prefers.json"):
    error = None
    print("попытка сохранения конфигурации")
    try:
        save_structure = {
            "theme": theme,
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
    print(theme)

    return theme

def first_save():
    save_config("light")