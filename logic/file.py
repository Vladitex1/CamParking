import json
import os

SAVEDIR = "../save/"


def save_data(polygons_list, filename="saved_data.txt", parentfile=None):
    error = None
    try:
        save_structure = {
            "polygons": polygons_list,
            "parent_file": parentfile
        }
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(save_structure, file, ensure_ascii=False, indent=2)
        return True,error
    except Exception as error:
        return False, error


def load_data(file_path: str = None):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        polygons_list = data.get("polygons", [])
        parent_file = data.get("parent_file", "")

        return True,polygons_list, parent_file

    except Exception as error:
        return False, error