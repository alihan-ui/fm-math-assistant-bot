import os
import json
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
 
# ─── НАСТРОЙКИ ───────────────────────────────────────────────────────────────
 
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "885045097"))
STATS_FILE = "stats.json"
MATERIALS_FILE = "materials.json"
 
bot = Bot(token=TOKEN)
dp = Dispatcher()
 
# ─── СОСТОЯНИЯ (FSM) ──────────────────────────────────────────────────────────
 
class AdminStates(StatesGroup):
    waiting_for_subject_name = State()
    waiting_for_material_file = State()
    waiting_for_material_name = State()
 
# ─── МАТЕРИАЛЫ И СТРУКТУРА ───────────────────────────────────────────────────
 
def load_materials():
    """Загрузить материалы из JSON"""
    if not os.path.exists(MATERIALS_FILE):
        return {
            "subjects": {
                "math": {
                    "name": "📐 Математика",
                    "emoji": "📐",
                    "materials": {}
                },
                "informatics": {
                    "name": "💻 Информатика",
                    "emoji": "💻",
                    "materials": {}
                },
                "physics": {
                    "name": "⚛️ Физика",
                    "emoji": "⚛️",
                    "materials": {}
                }
            },
            "proforientation": {
                "name": "🎯 Профориентация",
                "emoji": "🎯",
                "materials": {}
            }
        }
    with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
 
def save_materials(materials):
    """Сохранить материалы в JSON"""
    with open(MATERIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(materials, f, ensure_ascii=False, indent=2)
 
# ─── СТАТИСТИКА ──────────────────────────────────────────────────────────────
 
def load_stats():
    if not os.path.exists(STATS_FILE):
        return {"users": {}, "buttons": {}}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
 
def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
 
def track(user_id: int, first_name: str, button: str = None):
    """Отследить пользователя и нажатия кнопок"""
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
 
# ─── КЛАВИАТУРЫ ──────────────────────────────────────────────────────────────
 
def get_main_menu():
    """Главное меню - выбор предмета"""
    materials = load_materials()
    buttons = []
    
    # Кнопки предметов
    for subject_key, subject_data in materials["subjects"].items():
        buttons.append([KeyboardButton(text=subject_data["name"])])
    
    # Кнопка профориентации
    buttons.append([KeyboardButton(text=materials["proforientation"]["name"])])
    
    # Админ кнопка (если это админ)
    buttons.append([KeyboardButton(text="⚙️ Админ панель")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
 
def get_subject_menu(subject_key):
    """Меню внутри предмета"""
    materials = load_materials()
    subject = materials["subjects"].get(subject_key)
    
    if not subject:
        return None
    
    buttons = []
    
    # Материалы предмета
    for mat_key, mat_data in subject["materials"].items():
        buttons.append([KeyboardButton(text=f"📄 {mat_data['name']}")])
    
    if not subject["materials"]:
        buttons.append([KeyboardButton(text="⏳ Материалы скоро добавляются")])
    
    # Кнопка назад
    buttons.append([KeyboardButton(text="◀️ Назад в меню")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
 
def get_admin_menu():
    """Админ меню"""
    buttons = [
        [KeyboardButton(text="➕ Добавить материал")],
        [KeyboardButton(text="📋 Просмотр материалов")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="◀️ Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
 
# ─── КОМАНДЫ ──────────────────────────────────────────────────────────────────
 
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Команда /start"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    track(user_id, first_name)
    
    text = (
        "Сәлем 😊\n\n"
        "Бұл сіздің математикадан ҰБТ-ға дайындығыңызды жеңілдетуге арналған заманауи көмекшіңіз.\n\n"
        "Өзіңізге керекті батырманы басып, қажетті ақпаратты ала аласыз🫶🏻"
    )
    
    await message.answer(text, reply_markup=get_main_menu())
 
@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    """Команда /id - показать ID пользователя"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    
    track(user_id, first_name, "/id")
    
    await message.answer(f"🪪 Сіздің Telegram ID: `{user_id}`", parse_mode="Markdown")
 
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Команда /admin - админ панель"""
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
        f"📊 Админ панель\n\n"
        f"👥 Барлық пайдаланушылар: {total_users}\n"
        f"🆕 Бүгін жаңалар: {new_today}\n"
        f"🖱 Жалпы әрекеттер: {total_actions}\n\n"
        f"🔥 Топ-5 батырмалар:\n{top_text}"
    )
    
    await message.answer(text, reply_markup=get_admin_menu())
 
# ─── ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ───────────────────────────────────────────
 
@dp.message(F.text)
async def handle_text(message: types.Message, state: FSMContext):
    """Обработка всех текстовых сообщений"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    text = message.text.strip()
    
    # Проверка административных команд
    if user_id == ADMIN_ID:
        if text == "⚙️ Админ панель":
            track(user_id, first_name, "admin_panel")
            await message.answer("Админ панель открыта", reply_markup=get_admin_menu())
            return
        
        if text == "➕ Добавить материал":
            track(user_id, first_name, "add_material")
            materials = load_materials()
            
            # Показать список предметов для выбора
            buttons = []
            for subject_key, subject_data in materials["subjects"].items():
                buttons.append([KeyboardButton(text=subject_data["name"])])
            
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            await message.answer("Выбери предмет для добавления материала:", reply_markup=keyboard)
            await state.set_state(AdminStates.waiting_for_subject_name)
            return
        
        if text == "📋 Просмотр материалов":
            track(user_id, first_name, "view_materials")
            materials = load_materials()
            
            text_out = "📚 Все материалы:\n\n"
            for subject_key, subject_data in materials["subjects"].items():
                text_out += f"{subject_data['name']}:\n"
                if subject_data["materials"]:
                    for mat_key, mat_data in subject_data["materials"].items():
                        text_out += f"  • {mat_data['name']} (ID: {mat_key})\n"
                else:
                    text_out += "  (пусто)\n"
                text_out += "\n"
            
            await message.answer(text_out, reply_markup=get_admin_menu())
            return
        
        if text == "📊 Статистика":
            await cmd_admin(message)
            return
        
        if text == "◀️ Назад":
            await cmd_start(message)
            await state.clear()
            return
    
    # Обработка выбора предмета (админ добавляет материал)
    if await state.get_state() == AdminStates.waiting_for_subject_name:
        materials = load_materials()
        subject_key = None
        
        for key, data in materials["subjects"].items():
            if data["name"] == text:
                subject_key = key
                break
        
        if not subject_key:
            await message.answer("❌ Предмет не найден")
            return
        
        await state.update_data(subject_key=subject_key)
        await message.answer("Теперь отправь материал (PDF, видео, документ и т.д.)")
        await state.set_state(AdminStates.waiting_for_material_file)
        return
    
    # Обработка выбора предмета (пользователь просматривает)
    materials = load_materials()
    
    for subject_key, subject_data in materials["subjects"].items():
        if subject_data["name"] == text:
            track(user_id, first_name, f"select_{subject_key}")
            subject_menu = get_subject_menu(subject_key)
            
            if subject_menu:
                await message.answer(
                    f"Добро пожаловать в {subject_data['name']}!",
                    reply_markup=subject_menu
                )
            return
    
    # Профориентация
    if text == materials["proforientation"]["name"]:
        track(user_id, first_name, "proforientation")
        await message.answer(
            "🎯 Профориентация\n\n"
            "Этот раздел скоро будет дополнен чек-листами, гайдами и информацией о поступлении.",
            reply_markup=get_main_menu()
        )
        return
    
    # Назад в меню
    if text == "◀️ Назад в меню":
        await cmd_start(message)
        return
    
    # По умолчанию - вернуться в меню
    await cmd_start(message)
 
# ─── ОБРАБОТКА ФАЙЛОВ (для админа) ───────────────────────────────────────────
 
@dp.message(AdminStates.waiting_for_material_file)
async def handle_material_file(message: types.Message, state: FSMContext):
    """Получить файл материала"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Проверить что это файл
    if not message.document and not message.video and not message.audio and not message.photo:
        await message.answer("❌ Пожалуйста отправь файл (PDF, видео, фото и т.д.)")
        return
    
    # Получить file_id
    file_id = None
    file_type = None
    
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    
    await state.update_data(file_id=file_id, file_type=file_type)
    await message.answer("Как назвать этот материал? (например: 'Лекция 1 - Алгебра')")
    await state.set_state(AdminStates.waiting_for_material_name)
 
@dp.message(AdminStates.waiting_for_material_name)
async def handle_material_name(message: types.Message, state: FSMContext):
    """Сохранить материал с именем"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    subject_key = data.get("subject_key")
    file_id = data.get("file_id")
    file_type = data.get("file_type")
    material_name = message.text.strip()
    
    # Сохранить в materials.json
    materials = load_materials()
    
    # Создать уникальный ключ
    material_key = f"mat_{len(materials['subjects'][subject_key]['materials']) + 1}"
    
    materials["subjects"][subject_key]["materials"][material_key] = {
        "name": material_name,
        "file_id": file_id,
        "type": file_type,
        "added_date": str(date.today())
    }
    
    save_materials(materials)
    
    await message.answer(
        f"✅ Материал добавлен!\n\n"
        f"Предмет: {materials['subjects'][subject_key]['name']}\n"
        f"Имя: {material_name}\n"
        f"File ID: `{file_id}`\n"
        f"Тип: {file_type}",
        parse_mode="Markdown",
        reply_markup=get_admin_menu()
    )
    
    await state.clear()
 
# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────
 
async def main():
    """Запуск бота"""
    await dp.start_polling(bot)
 
if __name__ == "__main__":
    asyncio.run(main())
