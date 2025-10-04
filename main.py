import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (будет из переменных окружения)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8488877565:AAHVROf6p15vqVhIEkZ_QpLabDoVbk3cLpU")

# База данных (пока в памяти)
users = {}
tasks = [
    {"id": 1, "title": "📝 Написать отзыв", "reward": 10, "description": "Напишите отзыв о нашем проекте"},
    {"id": 2, "title": "🔔 Подписаться на канал", "reward": 5, "description": "Подпишитесь на наш Telegram канал"},
    {"id": 3, "title": "🌐 Перейти по ссылке", "reward": 3, "description": "Перейдите по указанной ссылке"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "level": 1,
            "completed_tasks": []
        }
    
    keyboard = [
        [InlineKeyboardButton("🎯 Доступные задания", callback_data="tasks")],
        [InlineKeyboardButton("💰 Мой баланс", callback_data="balance")],
        [InlineKeyboardButton("📊 Мой профиль", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name}!\n"
        f"Добро пожаловать в TaskBot!\n\n"
        f"Выполняй задания и зарабатывай деньги! 💰",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "tasks":
        await show_tasks(query, context)
    elif data == "balance":
        await show_balance(query, context)
    elif data == "profile":
        await show_profile(query, context)
    elif data.startswith("task_"):
        task_id = int(data.split("_")[1])
        await take_task(query, context, task_id)

async def show_tasks(query, context):
    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(
            f"{task['title']} - {task['reward']} монет",
            callback_data=f"task_{task['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 Доступные задания:\n\nВыберите задание для выполнения:",
        reply_markup=reply_markup
    )

async def show_balance(query, context):
    user_id = query.from_user.id
    user = users.get(user_id, {"balance": 0, "level": 1})
    
    await query.edit_message_text(
        f"💰 Ваш баланс: {user['balance']} монет\n\n"
        f"💵 Минимальный вывод: 50 рублей\n"
        f"📤 Вывод доступен с 5 уровня",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
    )

async def show_profile(query, context):
    user_id = query.from_user.id
    user = users.get(user_id, {"balance": 0, "level": 1, "completed_tasks": []})
    
    await query.edit_message_text(
        f"👤 Ваш профиль:\n\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Баланс: {user['balance']} монет\n"
        f"📊 Уровень: {user['level']}/25\n"
        f"✅ Выполнено заданий: {len(user['completed_tasks'])}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
    )

async def take_task(query, context, task_id):
    user_id = query.from_user.id
    task = next((t for t in tasks if t["id"] == task_id), None)
    
    if task:
        await query.edit_message_text(
            f"📋 Задание: {task['title']}\n\n"
            f"📝 Описание: {task['description']}\n"
            f"💰 Награда: {task['reward']} монет\n\n"
            f"После выполнения отправьте скриншот подтверждения!",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад к заданиям", callback_data="tasks")]])
        )

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    application.run_polling()
    print("Бот запущен!")

if name == "__main__":
    main()
