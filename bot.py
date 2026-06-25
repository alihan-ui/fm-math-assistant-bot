import asyncio
import json
import os
from datetime import datetime, date
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

import materials as mat
import admin
import github_sync

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "885045097"))

STATS_FILE = "stats.json"
bot = Bot(token=TOKEN)
dp = Dispatcher()

BACK_LABEL = "🔙 Артқа"

class NavStates(StatesGroup):
    browsing = State()

class AdminStates(StatesGroup):
    choosing_root = State()
    in_folder = State()
    input_folder_name = State()
    input_material_name = State()
    waiting_file = State()
    choosing_rename = State()
    input_new_name = State()
    choosing_delete = State()

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"users": {}, "buttons": {}}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def track(user_id: int, first_name: str, button: str = None):
    stats = load_stats()
    today = str(date.today())
    now = datetime.now().isoformat(timespec="seconds")
    user_id_str = str(user_id)

    if user_id_str not in stats["users"]:
        stats["users"][user_id_str] = {"name": first_name, "first_seen": today, "last_seen": now, "count": 0, "buttons": {}}

    u = stats["users"][user_id_str]
    u["name"] = first_name
    u["last_seen"] = now
    u["count"] = u.get("count", 0) + 1

    if button:
        u["buttons"][button] = u["buttons"].get(button, 0) + 1
        stats["buttons"][button] = stats["buttons"].get(button, 0) + 1

    save_stats(stats)

async def send_material(message: Message, file_id: str):
    await message.answer_document(file_id)
    await message.answer("Үздік нәтиже сізді күтеді 🏆\n\nДайындықты жалғастырамыс ба? 😇")

async def send_links(message: Message, title: str, links: list):
    numbered = "\n\n".join(f"{i+1}️⃣ {link}" for i, link in enumerate(links))
    await message.answer(f"{title}\n\n{numbered}")

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📐 Математика")],
    [KeyboardButton(text="💻 Информатика")],
    [KeyboardButton(text="⚛️ Физика")],
    [KeyboardButton(text="Саған қажетті заттар😉")],
], resize_keyboard=True)

admin_main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Статистика")],
    [KeyboardButton(text="⚙️ Админка")],
    [KeyboardButton(text="🔙 Артқа")],
], resize_keyboard=True)

ROOT_BUTTONS = {
    "📐 Математика": ["subjects", "math"],
    "💻 Информатика": ["subjects", "informatics"],
    "⚛️ Физика": ["subjects", "physics"],
    "Саған қажетті заттар😉": ["proforientation"],
}

def build_keyboard_for_node(node: dict) -> ReplyKeyboardMarkup:
    children = mat.list_children(node) or {}
    rows = [[KeyboardButton(text=child.get("label", key))] for key, child in children.items()]
    rows.append([KeyboardButton(text=BACK_LABEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def build_list_keyboard(node: dict) -> ReplyKeyboardMarkup:
    items = node.get("items", [])
    rows = [[KeyboardButton(text=item["label"])] for item in items]
    if not items:
        rows.append([KeyboardButton(text="⏳ Әзірге материал жоқ")])
    rows.append([KeyboardButton(text=BACK_LABEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

async def render_node(message: Message, state: FSMContext, path: list):
    data = mat.load_materials()
    node = mat.get_node(data, path)

    if node is None:
        await message.answer("⏳ Бөлім табылмады, басты мәзірге оралыңыз.", reply_markup=main_keyboard)
        await state.clear()
        return

    node_type = node.get("type")
    node_label = node.get("label", "?")

    if node_type == "coming_soon":
        await message.answer("⏳ Жақында қосылады!")
        return

    if node_type == "single":
        file_id = node.get("file_id")
        if file_id:
            await send_material(message, file_id)
        else:
            await message.answer("⏳ Материал жақында қосылады!")
        return

    if node_type == "list":
        await state.update_data(path=path)
        await state.set_state(NavStates.browsing)
        await message.answer(f"{node_label} бөлімін таңдаңыз😊:", reply_markup=build_list_keyboard(node))
        return

    children = mat.list_children(node)
    if children:
        await state.update_data(path=path)
        await state.set_state(NavStates.browsing)
        await message.answer(f"{node_label} бөлімін таңдаңыз:", reply_markup=build_keyboard_for_node(node))
        return

    await message.answer("⏳ Материал табылмады")

async def handle_list_item_click(message: Message, state: FSMContext, path: list, clicked_label: str) -> bool:
    data = mat.load_materials()
    node = mat.get_node(data, path)
    if not node or node.get("type") != "list":
        return False

    for item in node.get("items", []):
        if item.get("label") == clicked_label:
            track(message.from_user.id, message.from_user.first_name or "Қолданушы", clicked_label)
            if item.get("type") == "links":
                await send_links(message, item.get("title", clicked_label), item.get("links", []))
            else:
                file_id = item.get("file_id")
                if file_id:
                    await send_material(message, file_id)
                else:
                    await message.answer("⏳ Материал жақында қосылады!")
            return True
    return False

def parent_path(path: list) -> list:
    if len(path) <= 1:
        return []
    return path[:-1]

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name)
    await state.clear()

    await message.answer(
        "Сәлем 😊\n\n"
        "Бұл сіздің математикадан ҰБТ-ға дайындығыңызды жеңілдетуге арналған заманауи көмекшіңіз.\n\n"
        "Өзіңізге керекті батырманы басып, қажетті ақпаратты ала аласыз🫶🏻\n\n"
        "Қажетті бөлімді таңдаңыз😊:",
        reply_markup=main_keyboard
    )

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Сізге рұқсат жоқ")
        return
    await state.clear()
    await message.answer("📊 Админ панель ашылды:", reply_markup=admin_main_keyboard)

@dp.message(F.text == "⚙️ Админка")
async def admin_menu(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    roots = admin.get_root_folders()
    rows = [[KeyboardButton(text=f"{root_data.get('label', key)}")] for key, root_data in roots.items()]
    rows.append([KeyboardButton(text="➕ Добавить раздел")])
    rows.append([KeyboardButton(text="🔄 Переименовать раздел")])
    rows.append([KeyboardButton(text="❌ Удалить раздел")])
    rows.append([KeyboardButton(text="🔙 Артқа")])
    
    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await message.answer("Админка. Раздел таңдаңыз:", reply_markup=keyboard)
    await state.set_state(AdminStates.choosing_root)
    await state.update_data(root_folders=roots)

@dp.message(AdminStates.choosing_root)
async def admin_choose_root(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "🔙 Артқа":
        await message.answer("📊 Админ панель ашылды:", reply_markup=admin_main_keyboard)
        await state.clear()
        return

    if message.text == "➕ Добавить раздел":
        await message.answer("Жаңа раздел атын жазыңыз:")
        await state.set_state(AdminStates.input_folder_name)
        await state.update_data(action="add_root", path=[])
        return

    if message.text == "🔄 Переименовать раздел":
        roots = await state.get_data()
        roots = roots.get("root_folders", {})
        rows = [[KeyboardButton(text=f"{root_data.get('label', key)}")] for key, root_data in roots.items()]
        rows.append([KeyboardButton(text="🔙 Артқа")])
        keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
        await message.answer("Переименовать раздел таңдаңыз:", reply_markup=keyboard)
        await state.set_state(AdminStates.choosing_rename)
        await state.update_data(action="rename_root", path=[])
        return

    if message.text == "❌ Удалить раздел":
        roots = await state.get_data()
        roots = roots.get("root_folders", {})
        rows = [[KeyboardButton(text=f"{root_data.get('label', key)}")] for key, root_data in roots.items()]
        rows.append([KeyboardButton(text="🔙 Артқа")])
        keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
        await message.answer("Удалить раздел таңдаңыз:", reply_markup=keyboard)
        await state.set_state(AdminStates.choosing_delete)
        await state.update_data(action="delete_root", path=[])
        return

    data = admin.load_materials()
    roots = await state.get_data()
    roots = roots.get("root_folders", {})
    
    selected_key = None
    for key, root_data in roots.items():
        if root_data.get("label") == message.text:
            selected_key = key
            break
    
    if selected_key is None:
        await message.answer("❌ Раздел табылмады")
        return

    subjects = data.get("subjects", {})
    if selected_key in subjects:
        path = ["subjects", selected_key]
    else:
        path = [selected_key]
    
    await state.update_data(current_path=path)
    await show_folder_contents(message, state, path)

async def show_folder_contents(message: Message, state: FSMContext, path: list):
    if message.from_user.id != ADMIN_ID:
        return

    data = admin.load_materials()
    node = admin.get_node_by_path(data, path)
    
    if node is None:
        await message.answer("❌ Папка табылмады")
        return

    children, items, node_type = admin.list_children_and_items(node)
    node_label = node.get("label", path[-1] if path else "Root")

    rows = []
    
    for key, child in children.items():
        label = child.get("label", key)
        rows.append([KeyboardButton(text=label)])

    for item in items:
        label = item.get("label", "?")
        rows.append([KeyboardButton(text=f"📋 {label}")])

    if node_type == "folders":
        rows.append([KeyboardButton(text="➕ Добавить раздел")])
    elif node_type == "items":
        rows.append([KeyboardButton(text="📄 Добавить материал")])
    elif node_type == "mixed":
        rows.append([KeyboardButton(text="➕ Добавить раздел")])
        rows.append([KeyboardButton(text="📄 Добавить материал")])
    elif node_type == "unknown":
        rows.append([KeyboardButton(text="➕ Добавить раздел")])
        rows.append([KeyboardButton(text="📄 Добавить материал")])

    if children or items:
        rows.append([KeyboardButton(text="🔄 Переименовать")])
        rows.append([KeyboardButton(text="❌ Удалить")])

    rows.append([KeyboardButton(text="🔙 Назад")])

    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await message.answer(f"📂 {node_label}\n\nТаңдаңыз:", reply_markup=keyboard)
    
    await state.set_state(AdminStates.in_folder)
    await state.update_data(current_path=path, current_children=children, current_items=items, current_node_type=node_type)

@dp.message(AdminStates.in_folder)
async def admin_in_folder(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "🔙 Назад":
        data_state = await state.get_data()
        path = data_state.get("current_path", [])
        if len(path) > 1:
            await show_folder_contents(message, state, path[:-1])
        else:
            await admin_menu(message, state)
        return

    if message.text == "➕ Добавить раздел":
        await message.answer("Раздел атын жазыңыз:")
        await state.set_state(AdminStates.input_folder_name)
        await state.update_data(action="add_folder")
        return

    if message.text == "📄 Добавить материал":
        await message.answer("Материал атын жазыңыз:")
        await state.set_state(AdminStates.input_material_name)
        await state.update_data(action="add_item")
        return

    if message.text == "🔄 Переименовать":
        data_state = await state.get_data()
        children = data_state.get("current_children", {})
        items = data_state.get("current_items", [])

        rows = []
        for key, child in children.items():
            rows.append([KeyboardButton(text=child.get("label", key))])
        for item in items:
            rows.append([KeyboardButton(text=f"📋 {item.get('label')}")])
        rows.append([KeyboardButton(text="🔙 Артқа")])

        keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
        await message.answer("Переименовать таңдаңыз:", reply_markup=keyboard)
        await state.set_state(AdminStates.choosing_rename)
        await state.update_data(action="rename_in_folder")
        return

    if message.text == "❌ Удалить":
        data_state = await state.get_data()
        children = data_state.get("current_children", {})
        items = data_state.get("current_items", [])

        rows = []
        for key, child in children.items():
            rows.append([KeyboardButton(text=child.get("label", key))])
        for item in items:
            rows.append([KeyboardButton(text=f"📋 {item.get('label')}")])
        rows.append([KeyboardButton(text="🔙 Артқа")])

        keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
        await message.answer("Удалить таңдаңыз:", reply_markup=keyboard)
        await state.set_state(AdminStates.choosing_delete)
        await state.update_data(action="delete_in_folder")
        return

    data_state = await state.get_data()
    path = data_state.get("current_path", [])
    children = data_state.get("current_children", {})

    for key, child in children.items():
        if child.get("label") == message.text:
            await show_folder_contents(message, state, path + [key])
            return

    await message.answer("❓ Опция табылмады")

@dp.message(AdminStates.input_folder_name)
async def admin_input_folder_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    data_state = await state.get_data()
    action = data_state.get("action")
    path = data_state.get("current_path", [])
    folder_name = message.text

    data = admin.load_materials()

    if action == "add_root":
        folder_key = folder_name.lower().replace(" ", "_")
        if admin.add_root_folder(folder_key, folder_name):
            await message.answer(f"✅ Раздел '{folder_name}' қосылды!")
            await admin_menu(message, state)
        else:
            await message.answer("❌ Ошибка")
            await admin_menu(message, state)
        return

    if action == "add_folder":
        folder_key = folder_name.lower().replace(" ", "_")
        if admin.add_folder_to_node(data, path, folder_key, folder_name):
            admin.save_materials(data)
            await message.answer(f"✅ Раздел '{folder_name}' қосылды!")
            await show_folder_contents(message, state, path)
        else:
            await message.answer("❌ Ошибка")
            await show_folder_contents(message, state, path)
        return

@dp.message(AdminStates.input_material_name)
async def admin_input_material_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.update_data(material_name=message.text)
    await message.answer("Файлды жіберіңіз:")
    await state.set_state(AdminStates.waiting_file)

@dp.message(AdminStates.waiting_file)
async def admin_waiting_file(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.document and not message.video and not message.audio:
        await message.answer("❌ Файл жіберіңіз!")
        return

    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id

    data_state = await state.get_data()
    path = data_state.get("current_path", [])
    material_name = data_state.get("material_name", "?")

    data = admin.load_materials()
    if admin.add_item_to_node(data, path, material_name, file_id):
        admin.save_materials(data)
        
        status = "✅ Материал қосылды!"
        try:
            commit_sha = github_sync.commit_materials_json("materials.json", material_name)
            status += f"\n🚀 GitHub-ке жіберілді (commit {commit_sha})"
        except Exception as e:
            status += f"\n⚠️ GitHub: {str(e)[:50]}"
        
        await message.answer(f"{status}\n\n📋 File ID:\n`{file_id}`", parse_mode="Markdown")
        await show_folder_contents(message, state, path)
    else:
        await message.answer("❌ Ошибка")
        await show_folder_contents(message, state, path)

@dp.message(AdminStates.choosing_rename)
async def admin_choosing_rename(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "🔙 Артқа":
        data_state = await state.get_data()
        path = data_state.get("current_path", [])
        if path:
            await show_folder_contents(message, state, path)
        else:
            await admin_menu(message, state)
        return

    await state.update_data(rename_target=message.text)
    await message.answer("Жаңа атты жазыңыз:")
    await state.set_state(AdminStates.input_new_name)

@dp.message(AdminStates.input_new_name)
async def admin_input_new_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    data_state = await state.get_data()
    action = data_state.get("action", "")
    path = data_state.get("current_path", [])
    old_label = data_state.get("rename_target", "")
    new_label = message.text

    data = admin.load_materials()

    if action == "rename_root":
        roots = admin.get_root_folders()
        root_key = None
        for key, root_data in roots.items():
            if root_data.get("label") == old_label:
                root_key = key
                break
        if root_key and admin.rename_root_folder(root_key, new_label):
            await message.answer(f"✅ Переименовано!")
            await admin_menu(message, state)
        else:
            await message.answer("❌ Ошибка")
            await admin_menu(message, state)
        return

    if action == "rename_in_folder":
        node = admin.get_node_by_path(data, path)
        if node is None:
            await message.answer("❌ Ошибка")
            return

        found = False

        for key, child in list(node.items()):
            if key not in ("label", "type", "file_id", "items", "links", "title"):
                if isinstance(child, dict) and child.get("label") == old_label:
                    child["label"] = new_label
                    found = True
                    break

        if not found and node.get("type") == "list":
            for item in node.get("items", []):
                if item.get("label") == old_label:
                    item["label"] = new_label
                    found = True
                    break

        if found:
            admin.save_materials(data)
            await message.answer(f"✅ Переименовано!")
            await show_folder_contents(message, state, path)
        else:
            await message.answer("❌ Ошибка")
            await show_folder_contents(message, state, path)
        return

@dp.message(AdminStates.choosing_delete)
async def admin_choosing_delete(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "🔙 Артқа":
        data_state = await state.get_data()
        path = data_state.get("current_path", [])
        if path:
            await show_folder_contents(message, state, path)
        else:
            await admin_menu(message, state)
        return

    data_state = await state.get_data()
    action = data_state.get("action", "")
    path = data_state.get("current_path", [])
    target = message.text

    data = admin.load_materials()

    if action == "delete_root":
        roots = admin.get_root_folders()
        root_key = None
        for key, root_data in roots.items():
            if root_data.get("label") == target:
                root_key = key
                break
        if root_key and admin.delete_root_folder(root_key):
            await message.answer(f"✅ Удалено!")
            await admin_menu(message, state)
        else:
            await message.answer("❌ Ошибка")
            await admin_menu(message, state)
        return

    if action == "delete_in_folder":
        node = admin.get_node_by_path(data, path)
        if node is None:
            await message.answer("❌ Ошибка")
            return

        found = False

        for key in list(node.keys()):
            if key not in ("label", "type", "file_id", "items", "links", "title"):
                if isinstance(node[key], dict) and node[key].get("label") == target:
                    del node[key]
                    found = True
                    break

        if not found and node.get("type") == "list":
            for i, item in enumerate(node.get("items", [])):
                if item.get("label") == target or item.get("label") == target.replace("📋 ", ""):
                    node["items"].pop(i)
                    found = True
                    break

        if found:
            admin.save_materials(data)
            await message.answer(f"✅ Удалено!")
            await show_folder_contents(message, state, path)
        else:
            await message.answer("❌ Ошибка")
            await show_folder_contents(message, state, path)
        return

@dp.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stats = load_stats()
    today = str(date.today())
    users = stats.get("users", {})
    buttons = stats.get("buttons", {})

    total_users = len(users)
    new_today = sum(1 for u in users.values() if u.get("first_seen") == today)
    total_actions = sum(u.get("count", 0) for u in users.values())
    top_buttons = sorted(buttons.items(), key=lambda x: x[1], reverse=True)[:5]
    top_text = "\n".join(f"{i+1}. {b} — {c}" for i, (b, c) in enumerate(top_buttons)) or "—"

    text = f"📊 Статистика\n\n👥 Барлық пайдаланушылар: {total_users}\n🆕 Бүгін жаңалар: {new_today}\n🖱 Жалпы әрекеттер: {total_actions}\n\n🔥 Топ-5 батырмалар:\n{top_text}"
    await message.answer(text, reply_markup=admin_main_keyboard)

@dp.message(F.text.in_(ROOT_BUTTONS.keys()))
async def open_root_section(message: Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, message.text)

    path = ROOT_BUTTONS[message.text]
    await render_node(message, state, path)

@dp.message(F.text == "🔙 Артқа", NavStates.browsing)
async def back_inside_tree(message: Message, state: FSMContext):
    data = await state.get_data()
    current_path = data.get("path", [])
    target = parent_path(current_path)

    if not target:
        await state.clear()
        await message.answer("Қажетті бөлімді таңдаңыз😊:", reply_markup=main_keyboard)
        return

    await render_node(message, state, target)

@dp.message(NavStates.browsing)
async def navigate_tree(message: Message, state: FSMContext):
    data = await state.get_data()
    current_path = data.get("path", [])
    clicked = message.text

    full_data = mat.load_materials()
    current_node = mat.get_node(full_data, current_path)

    if current_node and current_node.get("type") == "list":
        handled = await handle_list_item_click(message, state, current_path, clicked)
        if handled:
            return
        await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇")
        return

    children = mat.list_children(current_node) or {}
    for key, child in children.items():
        child_label = child.get("label", key)
        if clicked == child_label:
            track(message.from_user.id, message.from_user.first_name or "Қолданушы", child_label)
            await render_node(message, state, current_path + [key])
            return

    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇")

@dp.message(F.text == "🔙 Артқа")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Қажетті бөлімді таңдаңыз😊:", reply_markup=main_keyboard)

@dp.message()
async def other(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇", reply_markup=main_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
