import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "885045097"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_material(message: Message, file_id: str):
    await message.answer_document(file_id)
    await message.answer(
        "Үздік нәтиже сізді күтеді 🏆\n\n"
        "Дайындықты жалғастырамыз ба? 😇"
    )

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📐 Математика")],
        [KeyboardButton(text="💻 Информатика")],
        [KeyboardButton(text="⚛️ Физика")],
        [KeyboardButton(text="🎯 Профориентация")],
    ],
    resize_keyboard=True
)

# МАТЕМАТИКА
formula_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="FM толық формула жинағы")],
        [KeyboardButton(text="Геометрия формулалары")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

prof_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Математика + Физика")],
        [KeyboardButton(text="Математика + Информатика")],
        [KeyboardButton(text="Математика + География")],
        [KeyboardButton(text="🔙 Басты мәзір")]
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
        [KeyboardButton(text="🔙 Басты мәзір")]
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
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

# ИНФОРМАТИКА (пусто, скоро добавляется)
informatics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏳ Жақында қосылады!")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

# ФИЗИКА (пусто, скоро добавляется)
physics_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏳ Жақында қосылады!")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

# МАТЕМАТИКА ГЛАВНОЕ МЕНЮ
math_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Формула жинақтары")],
        [KeyboardButton(text="📝 Нұсқа талдаулар")],
        [KeyboardButton(text="🎯 Мамандықтар тізімі")],
        [KeyboardButton(text="✅ Чек-листтер")],
        [KeyboardButton(text="🎥 12 сағаттық эфирлер")],
        [KeyboardButton(text="📚 Есеп жинақтары")],
        [KeyboardButton(text="📘 Гайдтар")],
        [KeyboardButton(text="📄 Спецификациялар")],
        [KeyboardButton(text="🔙 Басты мәзір")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Сәлем 😊\n\n"
        "Бұл сіздің математикадан ҰБТ-ға дайындығыңызды жеңілдетуге арналған заманауи көмекшіңіз.\n\n"
        "Өзіңізге керекті батырманы басып, қажетті ақпаратты ала аласыз🫶🏻\n\n"
        "Қажетті бөлімді таңдаңыз😊:",
        reply_markup=main_keyboard
    )

@dp.message(F.text == "🔙 Басты мәзір")
async def back(message: Message):
    await message.answer("Қажетті бөлімді таңдаңыз😊:", reply_markup=main_keyboard)

# МАТЕМАТИКА
@dp.message(F.text == "📐 Математика")
async def math_menu(message: Message):
    await message.answer("Математика бөлімін таңдаңыз:", reply_markup=math_keyboard)

@dp.message(F.text == "📖 Формула жинақтары")
async def formulas_menu(message: Message):
    await message.answer("Формула жинағын таңдаңыз😊:", reply_markup=formula_keyboard)

@dp.message(F.text == "FM толық формула жинағы")
async def formula_fm(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMhaivum6YUu_w_GDko4M6PzVnr3XoAAlqXAAKtAmBJEyCe1dt5fMw8BA")

@dp.message(F.text == "Геометрия формулалары")
async def formula_geo(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMvaivxMhJUprEoBPd54ZBRfF7X8AwAAoGXAAKtAmBJvfap8uuCIYQ8BA")

@dp.message(F.text == "📘 Гайдтар")
async def guides(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMPaivpCPcatwABXyOQ-45I4jWOoCyLAAL5lgACrQJgSd6V6xmqLzCxPAQ")

@dp.message(F.text == "📄 Спецификациялар")
async def specs(message: Message):
    await send_material(message, "BQACAgIAAxkBAAMNaivoYkVdTqn3-P_QtMVa_X52eNQAAvGWAAKtAmBJ1jlXPyhYHjU8BA")

@dp.message(F.text == "🎯 Мамандықтар тізімі")
async def professions(message: Message):
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

@dp.message(F.text == "✅ Чек-листтер")
async def checklists(message: Message):
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

@dp.message(F.text == "🎥 12 сағаттық эфирлер")
async def streams(message: Message):
    await message.answer(
        "🎥 12 сағаттық эфирлер\n\n"
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

@dp.message(F.text == "📝 Нұсқа талдаулар")
async def nuska(message: Message):
    await message.answer(
        "📝 Нұсқа талдаулар\n\n"
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

# ИНФОРМАТИКА
@dp.message(F.text == "💻 Информатика")
async def informatics_menu(message: Message):
    await message.answer("💻 Информатика", reply_markup=informatics_keyboard)

# ФИЗИКА
@dp.message(F.text == "⚛️ Физика")
async def physics_menu(message: Message):
    await message.answer("⚛️ Физика", reply_markup=physics_keyboard)

# ПРОФОРИЕНТАЦИЯ
@dp.message(F.text == "🎯 Профориентация")
async def proforientation(message: Message):
    await message.answer(
        "🎯 Профориентация\n\n"
        "Бұл бөлім жақында өндіктерлі болады.",
        reply_markup=main_keyboard
    )

@dp.message()
async def other(message: Message):
    await message.answer("Төмендегі батырмалар арқылы таңдаңыз 👇", reply_markup=main_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
