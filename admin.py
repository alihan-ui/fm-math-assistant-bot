"""
Новая рекурсивная админка для добавления/удаления разделов и материалов на любом уровне.
Поддерживает глубину вложенности до 10 уровней.
"""
import json
import os

MATERIALS_FILE = "materials.json"

def load_materials() -> dict:
    if not os.path.exists(MATERIALS_FILE):
        return {"subjects": {}, "proforientation": {}}
    with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_materials(data: dict) -> None:
    with open(MATERIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_node_by_path(data: dict, path: list[str]):
    """Получить узел по пути (список ключей)"""
    node = data
    for key in path:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return None
    return node

def set_node_by_path(data: dict, path: list[str], value):
    """Установить значение узла по пути"""
    if not path:
        return False
    node = data
    for key in path[:-1]:
        if key not in node:
            node[key] = {}
        node = node[key]
    node[path[-1]] = value
    return True

def list_children_and_items(node: dict):
    """
    Возвращает (children_dict, items_list, node_type)
    - children_dict: подузлы (папки) {key: {label, ...}}
    - items_list: материалы (файлы) [{label, file_id}, ...]
    - node_type: 'folders' | 'items' | 'mixed' | 'unknown'
    """
    if not isinstance(node, dict):
        return {}, [], "unknown"

    items = node.get("items", []) if node.get("type") == "list" else []

    children = {}
    for key, val in node.items():
        if key in ("label", "type", "file_id", "items", "links", "title"):
            continue
        if isinstance(val, dict) and "label" in val:
            children[key] = val

    if children and items:
        node_type = "mixed"
    elif children:
        node_type = "folders"
    elif items:
        node_type = "items"
    else:
        node_type = "unknown"

    return children, items, node_type

def add_folder_to_node(data: dict, path: list[str], folder_key: str, folder_label: str) -> bool:
    """Добавить подпапку в узел"""
    node = get_node_by_path(data, path)
    if node is None:
        return False
    node[folder_key] = {"label": folder_label}
    return True

def add_item_to_node(data: dict, path: list[str], item_label: str, file_id: str) -> bool:
    """Добавить материал в узел"""
    node = get_node_by_path(data, path)
    if node is None:
        return False
    if node.get("type") != "list":
        node["type"] = "list"
    if "items" not in node:
        node["items"] = []
    node["items"].append({"label": item_label, "file_id": file_id})
    return True

def rename_folder(data: dict, path: list[str], folder_key: str, new_label: str) -> bool:
    """Переименовать подпапку"""
    node = get_node_by_path(data, path)
    if node is None or folder_key not in node:
        return False
    node[folder_key]["label"] = new_label
    return True

def rename_item(data: dict, path: list[str], old_label: str, new_label: str) -> bool:
    """Переименовать материал"""
    node = get_node_by_path(data, path)
    if node is None or node.get("type") != "list":
        return False
    for item in node.get("items", []):
        if item.get("label") == old_label:
            item["label"] = new_label
            return True
    return False

def delete_folder(data: dict, path: list[str], folder_key: str) -> bool:
    """Удалить подпапку"""
    node = get_node_by_path(data, path)
    if node is None or folder_key not in node:
        return False
    del node[folder_key]
    return True

def delete_item(data: dict, path: list[str], item_label: str) -> bool:
    """Удалить материал"""
    node = get_node_by_path(data, path)
    if node is None or node.get("type") != "list":
        return False
    items = node.get("items", [])
    for i, item in enumerate(items):
        if item.get("label") == item_label:
            items.pop(i)
            return True
    return False

def get_root_folders() -> dict:
    """Получить корневые разделы (Математика, Информатика и т.д.)"""
    data = load_materials()
    subjects = data.get("subjects", {})
    prof = data.get("proforientation", {})
    
    root = {}
    for key, val in subjects.items():
        if isinstance(val, dict) and "label" in val:
            root[key] = val
    
    if isinstance(prof, dict) and "label" in prof:
        root["proforientation"] = prof
    
    return root

def add_root_folder(folder_key: str, folder_label: str) -> bool:
    """Добавить новый корневой раздел"""
    data = load_materials()
    if folder_key in data:
        return False
    data[folder_key] = {"label": folder_label}
    save_materials(data)
    return True

def rename_root_folder(folder_key: str, new_label: str) -> bool:
    """Переименовать корневой раздел"""
    data = load_materials()
    if folder_key not in data:
        return False
    data[folder_key]["label"] = new_label
    save_materials(data)
    return True

def delete_root_folder(folder_key: str) -> bool:
    """Удалить корневой раздел"""
    data = load_materials()
    if folder_key not in data:
        return False
    del data[folder_key]
    save_materials(data)
    return True
