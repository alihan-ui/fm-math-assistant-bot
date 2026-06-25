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
import github_sync

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "885045097"))

STATS_FILE = "stats.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

BACK_LABEL = "🔙 Артқа"  # кнопка "назад" внутри дерева материалов / в админке

# ════════════════════════════════════════════════════════════════════════════════
# СОСТОЯНИЯ (FSM)
# ════════════════════════════════════════════════════════════════════════════════

class AdminStates(StatesGroup):
    waiting_for_path = State()
    waiting_for_material_name = State()
    waiting_for_file = State()


class NavStates(StatesGroup):
    browsing = State()  # данные: path (list[str]) — текущий путь в дереве materials.json


# ════════════════════════════════════════════════════════════════════════════════
# СТАТИСТИКА
# ════════════════════════════════════════════════════════════════════════════════

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
        stats["users"][user_id_str] = {
            "name": first_name,
            "first_seen": today,
            "last_seen": now,
            "count": 0,
            "buttons": {}
        }

    u = stats["users"][user_id_str]
    u["name"] = first_name
    u["last_seen"] = now
    u["count"] = u.get("count", 0) + 1

    if button:
        u["buttons"][button] = u["buttons"].get(button, 0) + 1
        stats["buttons"][button] = stats["buttons"].get(button, 0) + 1

    save_stats(stats)


# ════════════════════════════════════════════════════════════════════════════════
# ОТПРАВКА МАТЕРИАЛОВ
# ════════════════════════════════════════════════════════════════════════════════

async def send_material(message: Message, file_id: str):
    await message.answer_document(file_id)
    await message.answer(
        "Үздік нәтиже сізді күтеді 🏆\n\n"
        "Дайындықты жалғастырамыс ба? 😇"
    )


async def send_links(message: Message, title: str, links: list[str]):
    numbered = "\n\n".join(f"{i+1}️⃣ {link}" for i, link in enumerate(links))
    await message.answer(f"{title}\n\n{numbered}")


# ════════════════════════════════════════════════════════════════════════════════
# СТАТИЧНЫЕ КЛАВИАТУРЫ (то, что вне дерева materials.json)
# ════════════════════════════════════════════════════════════════════════════════

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📐 Математика")],
        [KeyboardButton(text="💻 Информатика")],
        [KeyboardButton(text="⚛️ Физика")],
        [KeyboardButton(text="Саған қажетті заттар😉")],
    ],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Материал қосу")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🔙 Артқа")],
    ],
    resize_keyboard=True
)

# Корневые узлы дерева materials.json и подпись кнопки, которая в них ведёт
ROOT_BUTTONS = {
    "📐 Математика": ["subjects", "math"],
    "💻 Информатика": ["subjects", "informatics"],
    "⚛️ Физика": ["subjects", "physics"],
    "Саған қажетті заттар😉": ["proforientation"],
}


# ════════════════════════════════════════════════════════════════════════════════
# ДИНАМИЧЕСКАЯ НАВИГАЦИЯ ПО ДЕРЕВУ materials.json
# ════════════════════════════════════════════════════════════════════════════════

def build_keyboard_for_node(node: dict) -> ReplyKeyboardMarkup:
    """Строит клавиатуру из дочерних узлов (sections/subsections) текущего узла."""
    children = mat.list_children(node) or {}
    rows = []
    for key, child in children.items():
        label = child.get("label", key)
        if child.get("type") == "coming_soon" and "⏳" not in label:
            label = f"⏳ {label}"
        rows.append([KeyboardButton(text=label)])
    rows.append([KeyboardButton(text=BACK_LABEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def build_list_keyboard(node: dict) -> ReplyKeyboardMarkup:
    """Строит клавиатуру для узла type=list — кнопка на каждый item."""
    items = node.get("items", [])
    rows = [[KeyboardButton(text=item["label"])] for item in items]
    if not items:
        rows.append([KeyboardButton(text="⏳ Әзірге материал жоқ")])
    rows.append([KeyboardButton(text=BACK_LABEL)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def render_node(message: Message, state: FSMContext, path: list[str]):
    """Отображает узел дерева по пути: либо список подразделов, либо список материалов."""
    data = mat.load_materials()
    node = mat.get_node(data, path)

    if node is None:
        await message.answer("⏳ Бөлім табылмады, басты мәзірге оралыңыз.", reply_markup=main_keyboard)
        await state.clear()
        return

    node_type = node.get("type")

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
        await message.answer(
            f"{node.get('label', '')} бөлімін таңдаңыз😊:",
            reply_markup=build_list_keyboard(node)
        )
        return

    # Узел-папка (есть sections/subsections) — показываем подменю
    await state.update_data(path=path)
    await state.set_state(NavStates.browsing)
    await message.answer(
        f"{node.get('label', '')} бөлімін таңдаңыз:",
        reply_markup=build_keyboard_for_node(node)
    )


async def handle_list_item_click(message: Message, state: FSMContext, path: list[str], clicked_label: str) -> bool:
    """
    Если мы внутри узла type=list и пользователь нажал на один из items —
    отправляем материал/ссылки. Возвращает True если клик был обработан.
    """
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


def parent_path(path: list[str]) -> list[str]:
    """Путь родителя для кнопки 'Артқа'. Для верхнего уровня — пустой путь (главное меню)."""
    if len(path) <= 2:
        return []
    return path[:-1]


# ════════════════════════════════════════════════════════════════════════════════
# КОМАНДЫ
# ════════════════════════════════════════════════════════════════════════════════

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
    await message.answer("📊 Админ панель ашылды:", reply_markup=admin_keyboard)


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

    text = (
        f"📊 Статистика\n\n"
        f"👥 Барлық пайдаланушылар: {total_users}\n"
        f"🆕 Бүгін жаңалар: {new_today}\n"
        f"🖱 Жалпы әрекеттер: {total_actions}\n\n"
        f"🔥 Топ-5 батырмалар:\n{top_text}"
    )

    await message.answer(text, reply_markup=admin_keyboard)


# ════════════════════════════════════════════════════════════════════════════════
# АДМИНКА: ➕ Материал қосу (теперь пишет прямо в materials.json)
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "➕ Материал қосу")
async def add_material(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    data = mat.load_materials()
    paths = mat.collect_subject_paths(data)
    await state.update_data(admin_paths=paths)

    rows = [[KeyboardButton(text=label)] for _, label in paths]
    rows.append([KeyboardButton(text="🔙 Артқа")])
    keyboard = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await message.answer("Қай бөлімге материал қосамыз?", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_path)


@dp.message(AdminStates.waiting_for_path)
async def select_path(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "🔙 Артқа":
        await message.answer("📊 Админ панель ашылды:", reply_markup=admin_keyboard)
        await state.clear()
        return

    data = await state.get_data()
    paths = data.get("admin_paths", [])
    selected = next((p for p, label in paths if label == message.text), None)

    if selected is None:
        await message.answer("❌ Белгісіз бөлім. Тізімнен таңдаңыз:")
        return

    await state.update_data(target_path=selected)
    await message.answer("Материалдың атын жазыңыз (мысалы: 'Лекция 1 - Алгебра'):")
    await state.set_state(AdminStates.waiting_for_material_name)


@dp.message(AdminStates.waiting_for_material_name)
async def input_material_name(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.update_data(material_name=message.text)
    await message.answer("Енді файлды жіберіңіз (PDF, видео, құжат және т.б.):")
    await state.set_state(AdminStates.waiting_for_file)


@dp.message(AdminStates.waiting_for_file)
async def receive_file(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.document and not message.video and not message.audio and not message.photo:
        await message.answer("❌ Файлды жіберіңіз (PDF, видео, фото және т.б.)")
        return

    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    else:
        file_id = message.photo[-1].file_id
        file_type = "photo"

    data = await state.get_data()
    target_path = data.get("target_path")
    material_name = data.get("material_name")

    full_data = mat.load_materials()
    node = mat.get_node(full_data, target_path)
    node_type = node.get("type") if node else None

    if node_type == "single":
        ok = mat.set_single(full_data, target_path, file_id)
    else:
        ok = mat.add_item_to_list(full_data, target_path, material_name, file_id)

    if ok:
        mat.save_materials(full_data)
        status_line = "✅ materials.json-ге сақталды!"
        try:
            commit_sha = github_sync.commit_materials_json("materials.json", material_name)
            status_line += f"\n🚀 GitHub-ке жіберілді (commit {commit_sha}). Render автодеплой бастайды (~1-2 мин)."
        except github_sync.GithubCommitError as e:
            status_line += f"\n⚠️ GitHub-ке жіберу мүмкін болмады: {e}\n(materials.json локалда сақталды, бірақ келесі деплойда жоғалуы мүмкін!)"
        except Exception as e:
            status_line += f"\n⚠️ Күтпеген қате GitHub-пен байланыста: {e}"
    else:
        status_line = "⚠️ Бөлім табылмады, materials.json-ге сақталмады."

    text = (
        f"{status_line}\n\n"
        f"Бөлім: {' → '.join(target_path)}\n"
        f"Есімі: {material_name}\n"
        f"Түрі: {file_type}\n\n"
        f"📋 File ID:\n`{file_id}`"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard)
    await state.clear()


# ════════════════════════════════════════════════════════════════════════════════
# ОБЩАЯ КНОПКА "АРТҚА" (контекстная — зависит от состояния навигации)
# ════════════════════════════════════════════════════════════════════════════════

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


@dp.message(F.text == "🔙 Артқа")
async def back_default(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Қажетті бөлімді таңдаңыз😊:", reply_markup=main_keyboard)


# ════════════════════════════════════════════════════════════════════════════════
# ВХОД В КОРНЕВЫЕ РАЗДЕЛЫ (📐 Математика / 💻 Информатика / ⚛️ Физика / Саған қажетті заттар😉)
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text.in_(ROOT_BUTTONS.keys()))
async def open_root_section(message: Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, message.text)

    path = ROOT_BUTTONS[message.text]
    await render_node(message, state, path)


# ════════════════════════════════════════════════════════════════════════════════
# НАВИГАЦИЯ ВНУТРИ ДЕРЕВА (любой клик, когда мы в состоянии browsing)
# ════════════════════════════════════════════════════════════════════════════════

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
        if clicked in (child_label, f"⏳ {child_label}"):
            track(message.from_user.id, message.from_user.first_name or "Қолданушы", child_label)
            await render_node(message, state, current_path + [key])
            return

    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇")


# ════════════════════════════════════════════════════════════════════════════════
# FALLBACK
# ════════════════════════════════════════════════════════════════════════════════

@dp.message()
async def other(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇", reply_markup=main_keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
