"""
Работа с materials.json — структурой материалов бота.
Вместо хардкода кнопок и хендлеров под каждый файл, вся структура
(разделы, подразделы, file_id, ссылки) хранится в JSON и обрабатывается
универсальным движком в bot_with_admin.py.
"""
import json
import os
import threading

MATERIALS_FILE = "materials.json"
_lock = threading.Lock()


def load_materials() -> dict:
    if not os.path.exists(MATERIALS_FILE):
        return {"subjects": {}, "proforientation": {"label": "Саған қажетті заттар😉", "sections": {}}}
    with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_materials(data: dict) -> None:
    with _lock:
        tmp_path = MATERIALS_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, MATERIALS_FILE)


def get_node(data: dict, path: list[str]):
    """
    Достаёт узел дерева по пути.
    path — список ключей, например ["subjects", "math", "sections", "checklists"]
    """
    node = data
    for key in path:
        if isinstance(node, dict):
            if "sections" in node and key not in node and key in node.get("sections", {}):
                node = node["sections"][key]
                continue
            if "subsections" in node and key not in node and key in node.get("subsections", {}):
                node = node["subsections"][key]
                continue
            node = node.get(key)
        else:
            return None
        if node is None:
            return None
    return node


def list_children(node: dict):
    """
    Возвращает словарь {key: child_node} для дочерних узлов навигации
    (sections или subsections), либо None если узел — лист (list/single/coming_soon/links).
    """
    if not isinstance(node, dict):
        return None
    if "sections" in node:
        return node["sections"]
    if "subsections" in node:
        return node["subsections"]
    return None


def add_item_to_list(data: dict, path: list[str], label: str, file_id: str) -> bool:
    """Добавляет {label, file_id} в node['items'] по указанному пути. Создаёт items если нет."""
    node = get_node(data, path)
    if node is None:
        return False
    if node.get("type") not in ("list", None):
        node["type"] = "list"
    if "items" not in node:
        node["items"] = []
    # если материал с таким label уже есть — обновляем file_id, иначе добавляем
    for item in node["items"]:
        if item.get("label") == label:
            item["file_id"] = file_id
            return True
    node["items"].append({"label": label, "file_id": file_id})
    return True


def set_single(data: dict, path: list[str], file_id: str) -> bool:
    """Устанавливает file_id для узла типа single."""
    node = get_node(data, path)
    if node is None:
        return False
    node["type"] = "single"
    node["file_id"] = file_id
    return True


def collect_subject_paths(data: dict):
    """
    Возвращает плоский список (path, full_label) для всех листовых разделов
    (узлов с type == list/single), удобно для админ-меню "куда добавить материал".
    """
    results = []

    def walk(node, path, label_chain):
        if not isinstance(node, dict):
            return
        node_type = node.get("type")
        if node_type in ("list", "single"):
            results.append((path, " → ".join(label_chain)))
            return
        children = list_children(node)
        if children:
            for key, child in children.items():
                child_label = child.get("label", key)
                walk(child, path + [key], label_chain + [child_label])

    subjects = data.get("subjects", {})
    for subj_key, subj_node in subjects.items():
        subj_label = subj_node.get("label", subj_key)
        walk(subj_node, ["subjects", subj_key], [subj_label])

    prof = data.get("proforientation")
    if prof:
        prof_label = prof.get("label", "proforientation")
        walk(prof, ["proforientation"], [prof_label])

    return results
