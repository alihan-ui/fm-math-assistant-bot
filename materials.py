"""
Простой модуль для работы с materials.json — только чтение для пользователей.
Добавление/редактирование материалов происходит только через админку (admin.py).
"""
import json
import os

MATERIALS_FILE = "materials.json"

def load_materials() -> dict:
    if not os.path.exists(MATERIALS_FILE):
        return {"subjects": {}, "proforientation": {}}
    with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_node(data: dict, path: list[str]):
    """Получить узел по пути"""
    node = data
    for key in path:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return None
    return node

def list_children(node: dict):
    """
    Возвращает словарь подузлов (папок).
    Подузлы — это dict с "label" ключом (но без "type":"list").
    """
    if not isinstance(node, dict):
        return None
    
    children = {}
    for key, val in node.items():
        if key in ("label", "type", "file_id", "items", "links", "title"):
            continue
        if isinstance(val, dict) and "label" in val:
            children[key] = val
    
    return children if children else None
