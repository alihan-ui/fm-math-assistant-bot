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

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "885045097"))

STATS_FILE = "stats.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ════════════════════════════════════════════════════════════════════════════════
# СОСТОЯНИЯ (FSM) для админки
# ════════════════════════════════════════════════════════════════════════════════

class AdminStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_material_name = State()
    waiting_for_file = State()

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

# ════════════════════════════════════════════════════════════════════════════════
# ОТПРАВКА МАТЕРИАЛОВ
# ════════════════════════════════════════════════════════════════════════════════

async def send_material(message: Message, file_id: str):
    await message.answer_document(file_id)
    await message.answer(
        "Үздік нәтиже сізді күтеді 🏆\n\n"
        "Дайындықты жалғастырамыс ба? 😇"
    )

# ════════════════════════════════════════════════════════════════════════════════
# КЛАВИАТУРЫ
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

subject_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📐 Математика")],
        [KeyboardButton(text="💻 Информатика")],
        [KeyboardButton(text="⚛️ Физика")],
        [KeyboardButton(text="🔙 Артқа")],
    ],
    resize_keyboard=True
)

math_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Формула жинақтары")],
        [KeyboardButton(text="🎥 Эфирлер")],
        [KeyboardButton(text="✅ Чек-листтер")],
        [KeyboardButton(text="📚 Есеп жинақтары")],
        [KeyboardButton(text="📄 Спецификациялар")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

formula_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="FM толық формула жинағы")],
        [KeyboardButton(text="Геометрия формулалары")],
        [KeyboardButton(text="🔙 Математикаға қайту")]
    ],
    resize_keyboard=True
)

math_streams_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Нұсқа талдаулар")],
        [KeyboardButton(text="12 сағаттық эфирлер")],
        [KeyboardButton(text="🔙 Математикаға қайту")]
    ],
    resize_keyboard=True
)

check_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Стереометрия")],
        [KeyboardButton(text="Интеграл")],
        [KeyboardButton(text="Модуль және теңсіздіктер")],
        [KeyboardButton(text="Пайыз табу")],
        [KeyboardButton(text="Дәреже және оның қасиеттері")],
        [KeyboardButton(text="ЕКОЕ және ЕҮОБ")],
        [KeyboardButton(text="🔙 Математикаға қайту")]
    ],
    resize_keyboard=True
)

books_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рустюмова")],
        [KeyboardButton(text="Қызыл кітап 1")],
        [KeyboardButton(text="Scanavi Қазақша")],
        [KeyboardButton(text="Skanavi gruppa V yechimlari")],
        [KeyboardButton(text="Skanavi Gruppa A yechimlari")],
        [KeyboardButton(text="🔙 Математикаға қайту")]
    ],
    resize_keyboard=True
)

informatics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎥 Эфирлер")],
        [KeyboardButton(text="📝 Тапсырмалар")],
        [KeyboardButton(text="📚 Теориялық базалар")],
        [KeyboardButton(text="✅ Чек-листтер")],
        [KeyboardButton(text="📄 Спецификация")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

informatics_streams_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Нұсқа талдаулар")],
        [KeyboardButton(text="12 сағаттық эфирлер")],
        [KeyboardButton(text="Тақырыптық талдаулар")],
        [KeyboardButton(text="🔙 Информатикаға қайту")]
    ],
    resize_keyboard=True
)

informatics_tasks_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тақырыптық тапсырмалар")],
        [KeyboardButton(text="Нұсқалар")],
        [KeyboardButton(text="🔙 Информатикаға қайту")]
    ],
    resize_keyboard=True
)

physics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏳ Жақында қосылады!")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

proforientation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Мамандықтар тізімі")],
        [KeyboardButton(text="📘 Гайдтар")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

prof_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Математика + Физика")],
        [KeyboardButton(text="Математика + Информатика")],
        [KeyboardButton(text="Математика + География")],
        [KeyboardButton(text="🔙 Профориентацияға қайту")]
    ],
    resize_keyboard=True
)

# ════════════════════════════════════════════════════════════════════════════════
# КОМАНДЫ
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name)
    
    await message.answer(
        "Сәлем 😊\n\n"
        "Бұл сіздің математикадан ҰБТ-ға дайындығыңызды жеңілдетуге арналған заманауи көмекшіңіз.\n\n"
        "Өзіңізге керекті батырманы басып, қажетті ақпаратты ала аласыз🫶🏻\n\n"
        "Қажетті бөлімді таңдаңыз😊:",
        reply_markup=main_keyboard
    )

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админ панель"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Сізге рұқсат жоқ")
        return
    
    await message.answer("📊 Админ панель ашылды:", reply_markup=admin_keyboard)

@dp.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    """Показать статистику"""
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

@dp.message(F.text == "➕ Материал қосу")
async def add_material(message: Message, state: FSMContext):
    """Начать добавление материала"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("Предметті таңдаңыз:", reply_markup=subject_keyboard)
    await state.set_state(AdminStates.waiting_for_subject)

@dp.message(AdminStates.waiting_for_subject)
async def select_subject(message: Message, state: FSMContext):
    """Выбор предмета"""
    if message.from_user.id != ADMIN_ID:
        return
    
    subject = message.text
    
    if subject not in ["📐 Математика", "💻 Информатика", "⚛️ Физика", "🔙 Артқа"]:
        await message.answer("❌ Белгісіз предмет. Қайта таңдаңыз:")
        return
    
    if subject == "🔙 Артқа":
        await message.answer("📊 Админ панель ашылды:", reply_markup=admin_keyboard)
        await state.clear()
        return
    
    await state.update_data(subject=subject)
    await message.answer(f"Материалдың атын жазыңыз (мысалы: 'Лекция 1 - Алгебра'):")
    await state.set_state(AdminStates.waiting_for_material_name)

@dp.message(AdminStates.waiting_for_material_name)
async def input_material_name(message: Message, state: FSMContext):
    """Ввод названия материала"""
    if message.from_user.id != ADMIN_ID:
        return
    
    material_name = message.text
    await state.update_data(material_name=material_name)
    await message.answer(f"Енді файлды жіберіңіз (PDF, видео, құжат және т.б.):")
    await state.set_state(AdminStates.waiting_for_file)

@dp.message(AdminStates.waiting_for_file)
async def receive_file(message: Message, state: FSMContext):
    """Получение файла"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Проверить что это файл
    if not message.document and not message.video and not message.audio and not message.photo:
        await message.answer("❌ Файлды жіберіңіз (PDF, видео, фото және т.б.)")
        return
    
    # Получить file_id
    file_id = None
    file_type = None
    file_name = None
    
    if message.document:
        file_id = message.document.file_id
        file_type = "document"
        file_name = message.document.file_name or "document"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
        file_name = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
        file_name = "audio"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
        file_name = "photo"
    
    data = await state.get_data()
    subject = data.get("subject")
    material_name = data.get("material_name")
    
    text = (
        f"✅ Материал қосылды!\n\n"
        f"Предмет: {subject}\n"
        f"Есімі: {material_name}\n"
        f"Түрі: {file_type}\n\n"
        f"📋 File ID:\n`{file_id}`"
    )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard)
    await state.clear()

@dp.message(F.text == "🔙 Артқа")
async def back_main(message: Message):
    await message.answer("Қажетті бөлімді таңдаңыз😊:", reply_markup=main_keyboard)

# ════════════════════════════════════════════════════════════════════════════════
# МАТЕМАТИКА HANDLERS
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "📐 Математика")
async def math_menu(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "math")
    await message.answer("Математика бөлімін таңдаңыз:", reply_markup=math_keyboard)

@dp.message(F.text == "🔙 Математикаға қайту")
async def back_math(message: Message):
    await message.answer("Математика бөлімін таңдаңыз:", reply_markup=math_keyboard)

@dp.message(F.text == "📖 Формула жинақтары")
async def formulas_menu(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "formulas")
    await message.answer("Формула жинағын таңдаңыз😊:", reply_markup=formula_keyboard)

@dp.message(F.text == "FM толық формула жинағы")
async def formula_fm(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMhaivum6YUu_w_GDko4M6PzVnr3XoAAlqXAAKtAmBJEyCe1dt5fMw8BA")

@dp.message(F.text == "Геометрия формулалары")
async def formula_geo(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMvaivxMhJUprEoBPd54ZBRfF7X8AwAAoGXAAKtAmBJvfap8uuCIYQ8BA")

@dp.message(F.text == "📄 Спецификациялар")
async def specs(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "specs")
    await send_material(message, "BQACAgIAAxkBAAMNaivoYkVdTqn3-P_QtMVa_X52eNQAAvGWAAKtAmBJ1jlXPyhYHjU8BA")

@dp.message(F.text == "✅ Чек-листтер")
async def checklists(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "checklists")
    await message.answer("Чек-лист таңдаңыз😊:", reply_markup=check_keyboard)

@dp.message(F.text == "Стереометрия")
async def ch1(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMjaivvStywIWtpCrX8CryUl21GEm4AAmKXAAKtAmBJv_VbrGFO3wc8BA")

@dp.message(F.text == "Интеграл")
async def ch2(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMlaivvSsteogbS9PB8AV3ri5lZ3_EAAmSXAAKtAmBJPUKf_9C7dq48BA")

@dp.message(F.text == "Модуль және теңсіздіктер")
async def ch3(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMkaivvSnxVWJTw6jgVTwqr3IyO-JkAAmOXAAKtAmBJY5WEFvycxQk8BA")

@dp.message(F.text == "Пайыз табу")
async def ch4(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMoaivvSrXOH3jC9Iq8G6nH5ebHIgwAAmeXAAKtAmBJj6kUMP0sMnM8BA")

@dp.message(F.text == "Дәреже және оның қасиеттері")
async def ch5(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMnaivvSiQX3MDb-hqJxnXOz0BUp5gAAmaXAAKtAmBJzqPQ-65iL208BA")

@dp.message(F.text == "ЕКОЕ және ЕҮОБ")
async def ch6(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMmaivvSn3f2_ErLq0ZvVNhBn08KowAAmWXAAKtAmBJocCXGDW3aBU8BA")

@dp.message(F.text == "📚 Есеп жинақтары")
async def books(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "books")
    await message.answer("Есеп жинағын таңдаңыз😊:", reply_markup=books_keyboard)

@dp.message(F.text == "Рустюмова")
async def book1(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMXaivt37EPRojRpgWbd18HL_j-zUIAAkWXAAKtAmBJMP0iSpLBcbw8BA")

@dp.message(F.text == "Қызыл кітап 1")
async def book2(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMZaivt6tI4aqmns5UeHSMS9xTEo0oAAkuXAAKtAmBJgeZL3K2UUS48BA")

@dp.message(F.text == "Scanavi Қазақша")
async def book3(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMbaivt8TFdKhylKTTQA10nIvwTCEgAAkyXAAKtAmBJw3REgOJlUTU8BA")

@dp.message(F.text == "Skanavi gruppa V yechimlari")
async def book4(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMdaivt8aqFJN82IQ21j7nAUNoZMT8AAk6XAAKtAmBJjMD6It2TnVw8BA")

@dp.message(F.text == "Skanavi Gruppa A yechimlari")
async def book5(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMzaivyMoFWUYDCat3bxIbg3qrHjXQAApuXAAKtAmBJk6ScWJxHWlY8BA")

# Эфирлер в Математике
@dp.message(F.text == "🎥 Эфирлер")
async def math_streams(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "streams")
    await message.answer("Эфирлерді таңдаңыз😊:", reply_markup=math_streams_keyboard)

@dp.message(F.text == "🔙 Профориентацияға қайту")
async def back_prof(message: Message):
    await message.answer("Мамандықтар мен гайдтарды таңдаңыз😊:", reply_markup=proforientation_keyboard)

@dp.message(F.text == "Нұсқа талдаулар")
async def math_nuska(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "nuska")
    await message.answer(
        "📝 Нұсқа талдаулар (Математика)\n\n"
        "1️⃣ https://www.youtube.com/live/X8E_LKEvCQQ\n\n"
        "2️⃣ https://www.youtube.com/live/Hr_Lcc8SDrA\n\n"
        "3️⃣ https://www.youtube.com/live/qszjXWW-kzg\n\n"
        "4️⃣ https://www.youtube.com/live/RBI30Sl7znE\n\n"
        "5️⃣ https://www.youtube.com/live/dT0Zusf1q58\n\n"
        "6️⃣ https://www.youtube.com/live/GToZYK7EGqQ\n\n"
        "7️⃣ https://youtu.be/J4u4xVYWTKk\n\n"
        "8️⃣ https://www.youtube.com/live/WX3s4lVT_Do\n\n"
        "9️⃣ https://www.youtube.com/live/fCnZPZ1Rw7w\n\n"
        "🔟 https://www.youtube.com/live/W5PhjoWd77c\n\n"
        "1️⃣1️⃣ https://www.youtube.com/live/dpzWNqCqL8k"
    )

@dp.message(F.text == "12 сағаттық эфирлер")
async def math_12streams(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "12_streams")
    await message.answer(
        "🎥 12 сағаттық эфирлер (Математика)\n\n"
        "1️⃣ https://www.youtube.com/live/5ZJyxKkKKM0\n\n"
        "2️⃣ https://www.youtube.com/live/8g4nBZuqSyg\n\n"
        "3️⃣ https://www.youtube.com/live/LQI2qCXN2R4\n\n"
        "4️⃣ https://www.youtube.com/live/4JrjVvrqA6Y\n\n"
        "5️⃣ https://www.youtube.com/live/v4ViVRkwfPM\n\n"
        "6️⃣ https://www.youtube.com/live/Py9KJ88uvQs\n\n"
        "7️⃣ https://www.youtube.com/live/AEaxkQJ9C_E\n\n"
        "8️⃣ https://www.youtube.com/live/7iWfTWMcnZY\n\n"
        "9️⃣ https://www.youtube.com/live/W2vAd0WphBo\n\n"
        "🔟 https://www.youtube.com/live/D4R6tUm40LU"
    )

# ════════════════════════════════════════════════════════════════════════════════
# ИНФОРМАТИКА HANDLERS
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "💻 Информатика")
async def informatics_menu(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "informatics")
    await message.answer("💻 Информатика бөлімін таңдаңыз:", reply_markup=informatics_keyboard)

@dp.message(F.text == "🔙 Информатикаға қайту")
async def back_informatics(message: Message):
    await message.answer("💻 Информатика бөлімін таңдаңыз:", reply_markup=informatics_keyboard)

# Эфирлер в Информатике - используем ту же функцию но с разными текстами
@dp.message(F.text == "Тақырыптық талдаулар")
async def inf_topical(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "topical")
    await message.answer(
        "🎥 Тақырыптық талдаулар (Информатика)\n\n"
        "1️⃣ https://www.youtube.com/live/wHGtPQI7uO4?si=VS2cNtrDhxDGAvyu\n\n"
        "2️⃣ https://www.youtube.com/live/4X3qeVjdZo4?si=w8gbf8iOFk5yjDVs\n\n"
        "3️⃣ https://www.youtube.com/live/yIWe32DF2Fw?si=jIyH-ANQLAvT1CmF\n\n"
        "4️⃣ https://www.youtube.com/live/w7RNWSTLzlg?si=LWerSVKGuDT8L_Sw\n\n"
        "5️⃣ https://www.youtube.com/live/TdtVoi4D7tA?si=zfOOndihhjwowYHe\n\n"
        "6️⃣ https://www.youtube.com/live/sWqgV1lj3so?si=ydRyeeocHArqfsdB"
    )

# Тапсырмалар
@dp.message(F.text == "📝 Тапсырмалар")
async def informatics_tasks(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "tasks")
    await message.answer("Тапсырмалар түрін таңдаңыз😊:", reply_markup=informatics_tasks_keyboard)

@dp.message(F.text == "Тақырыптық тапсырмалар")
async def inf_topical_tasks(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "topical_tasks")
    await message.answer("⏳ Материал жақында қосылады!", reply_markup=informatics_tasks_keyboard)

# Теориялық базалар
@dp.message(F.text == "📚 Теориялық базалар")
async def inf_theory(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "theory")
    await message.answer("⏳ Материал жақында қосылады!", reply_markup=informatics_keyboard)

# Спецификация в Информатике
@dp.message(F.text == "📄 Спецификация")
async def inf_specs(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "inf_specs")
    await message.answer("⏳ Материал жақында қосылады!", reply_markup=informatics_keyboard)

# ════════════════════════════════════════════════════════════════════════════════
# ФИЗИКА
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "⚛️ Физика")
async def physics_menu(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "physics")
    await message.answer("⚛️ Физика", reply_markup=physics_keyboard)

# ════════════════════════════════════════════════════════════════════════════════
# ПРОФОРИЕНТАЦИЯ
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "Саған қажетті заттар😉")
async def proforientation(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "proforientation")
    await message.answer("Мамандықтар мен гайдтарды таңдаңыз😊:", reply_markup=proforientation_keyboard)

@dp.message(F.text == "🎯 Мамандықтар тізімі")
async def professions(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "professions")
    await message.answer("Бағытты таңдаңыз😊:", reply_markup=prof_keyboard)

@dp.message(F.text == "Математика + Физика")
async def prof_phys(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMTaivspfgwUqgcE-nCk37sZ0gO4SYAAiuXAAKtAmBJpnCkhOKSZtA8BA")

@dp.message(F.text == "Математика + Информатика")
async def prof_info(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMSaivspeEzhdsdLQYzJQ6s3wwrmqIAAiqXAAKtAmBJ07JWBgNAsME8BA")

@dp.message(F.text == "Математика + География")
async def prof_geo(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMRaivspUaFPGPg8CVR9G5T5oA197AAAimXAAKtAmBJLZ08FZYxLtQ8BA")

@dp.message(F.text == "📘 Гайдтар")
async def guides(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Қолданушы"
    track(user_id, first_name, "guides")
    await send_material(message, "BQACAgIAAxkBAAMPaivpCPcatwABXyOQ-45I4jWOoCyLAAL5lgACrQJgSd6V6xmqLzCxPAQ")

# ════════════════════════════════════════════════════════════════════════════════
# FALLBACK
# ════════════════════════════════════════════════════════════════════════════════

@dp.message()
async def other(message: Message):
    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇", reply_markup=main_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
