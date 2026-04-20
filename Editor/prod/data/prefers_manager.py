import json
import os

# Убедимся, что папка существует
userdata_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user"))
os.makedirs(userdata_directory, exist_ok=True)


def save_config(filename="prefers.json", **kwargs):
    if filename == 0:
        filename = "prefers.json"
    filepath = os.path.join(userdata_directory, filename)

    # 1. Сначала пытаемся прочитать текущий конфиг БЕЗ вызова load_config()
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding='utf-8') as file:
                data = json.load(file)
        except (json.JSONDecodeError, ValueError):
            data = {}

    # 2. Обновляем данные (только те, что передали в функцию)
    # Используем "is not None", чтобы пустая строка "" могла быть сохранена
    for key, value in kwargs.items():
        if value is not None:
            data[key] = value

    # 3. Сохраняем итоговый словарь
    try:
        with open(filepath, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True, None
    except Exception as e:
        print(f"Ошибка записи: {e}")
        return False, e


def load_config(filename: str = "prefers.json"):
    filepath = os.path.join(userdata_directory, filename)

    if not os.path.exists(filepath):
        print("Файл не найден, создаем значения по умолчанию...")
        return first_save(filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print("Файл поврежден, сброс до настроек по умолчанию")
        return first_save(filename)

    # Используем .get(ключ, ""), чтобы не было KeyError
    return {
        "client_theme": data.get("client_theme", ""),
        "client_language": data.get("client_language", ""),
        "client_fast_navigation": data.get("client_fast_navigation", ""),
        "client_debug": data.get("client_debug", ""),
        "camera_ip": data.get("camera_ip", ""),
        "camera_port": data.get("camera_port", ""),
        "camera_login": data.get("camera_login", ""),
        "camera_pass": data.get("camera_pass", ""),
        "camera_stream_path": data.get("camera_stream_path", ""),
    }


def first_save(filename="prefers.json"):
    # Передаем все стартовые значения
    defaults = {
        "client_theme": "light",
        "client_language": "RU",
        "client_fast_navigation": False,
        "client_debug": False,
        "camera_ip": "192.168.0.27",
        "camera_port": "554",
        "camera_login": "admin",
        "camera_pass": "",
        "camera_stream_path": "stream1"
    }
    save_config(filename=filename, **defaults)
    return defaults