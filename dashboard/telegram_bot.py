import os
import sys
import django
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cortex.settings')
django.setup()

from django.conf import settings
from dashboard.models import UserProfile
from dashboard.models import Note, Deadline, Goal

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        return profile.user
    except UserProfile.DoesNotExist:
        return None

@sync_to_async
def process_binding_code(code, telegram_id):
    """Привязывает Telegram ID к пользователю по коду. Возвращает (успех, сообщение)."""
    try:
        profile = UserProfile.objects.get(binding_code=code)
        if profile.telegram_id:
            return False, "Этот аккаунт уже привязан к другому Telegram."
        profile.telegram_id = telegram_id
        profile.binding_code = None  # делаем код одноразовым
        profile.save()
        return True, f"Telegram успешно привязан к аккаунту {profile.user.username}!"
    except UserProfile.DoesNotExist:
        return False, "Неверный код привязки. Проверьте и попробуйте снова."

@sync_to_async
def get_all_user_data(user):
    goals = list(Goal.objects.filter(user=user))
    notes = list(Note.objects.filter(user=user))
    deadlines = list(Deadline.objects.filter(user=user))
    return {'goals': goals, 'notes': notes, 'deadlines': deadlines}

@sync_to_async
def add_goal_to_db(user, title):
    Goal.objects.create(user=user, title=title)

@sync_to_async
def add_note_to_db(user, title):
    Note.objects.create(user=user, title=title)

@sync_to_async
def get_user_goals(user):
    return list(Goal.objects.filter(user=user))

@sync_to_async
def get_user_notes(user):
    return list(Note.objects.filter(user=user))

@sync_to_async
def get_user_deadlines(user):
    return list(Deadline.objects.filter(user=user))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        await update.message.reply_text("Вы уже подключены к Cortex! Используйте /info для просмотра данных.")
    else:
        await update.message.reply_text(
            "Добро пожаловать в Cortex!\n\n"
            "Чтобы привязать ваш Telegram-аккаунт:\n"
            "1. Зарегистрируйтесь на сайте\n"
            "2. Скопируйте код привязки из личного кабинета\n"
            "3. Отправьте его сюда"
        )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены. Отправьте код привязки или напишите /start.")
        return

    data = await get_all_user_data(user)
    goals_text = "\n".join(f"- {g.title}" for g in data['goals']) or "Нет целей."
    notes_text = "\n".join(f"- {n.title}" for n in data['notes']) or "Нет заметок."
    deadlines_text = "\n".join(
        f"- {d.title} ({d.due_date.strftime('%d.%m.%Y %H:%M') if d.due_date else 'без срока'})"
        for d in data['deadlines']
    ) or "Нет дедлайнов."

    text = f"""
Ваши данные в Cortex:

ЦЕЛИ:
{goals_text}

ЗАМЕТКИ:
{notes_text}

ДЕДЛАЙНЫ:
{deadlines_text}
    """.strip()
    await update.message.reply_text(text)

async def add_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены. Отправьте код привязки.")
        return

    goal_text = " ".join(context.args)
    if not goal_text:
        await update.message.reply_text("Использование: /add_goal Название цели")
        return

    await add_goal_to_db(user, goal_text)
    await update.message.reply_text(f"Цель '{goal_text}' добавлена!")

async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены. Отправьте код привязки.")
        return

    note_text = " ".join(context.args)
    if not note_text:
        await update.message.reply_text("Использование: /add_note Название заметки")
        return

    await add_note_to_db(user, note_text)
    await update.message.reply_text(f"Заметка '{note_text}' добавлена!")

async def goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены.")
        return
    goals_list = await get_user_goals(user)
    text = "Ваши цели:\n" + "\n".join(f"- {g.title}" for g in goals_list) if goals_list else "Нет целей."
    await update.message.reply_text(text)

async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены.")
        return
    notes_list = await get_user_notes(user)
    text = "Ваши заметки:\n" + "\n".join(f"- {n.title}" for n in notes_list) if notes_list else "Нет заметок."
    await update.message.reply_text(text)

async def deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await update.message.reply_text("Вы не подключены.")
        return
    deadlines_list = await get_user_deadlines(user)
    text = "Ваши дедлайны:\n" + "\n".join(
        f"- {d.title} ({d.due_date.strftime('%d.%m.%Y %H:%M') if d.due_date else 'без срока'})"
        for d in deadlines_list
    ) if deadlines_list else "Нет дедлайнов."
    await update.message.reply_text(text)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        # Пользователь уже привязан — игнорируем обычные сообщения
        await update.message.reply_text("Вы уже подключены! Используйте команды: /info, /goals, /add_goal и т.д.")
        return

    text = update.message.text.strip()
    # Предполагаем, что любое текстовое сообщение — это код привязки
    success, message = await process_binding_code(text, telegram_id)
    await update.message.reply_text(message)

def run_telegram_bot():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("add_goal", add_goal))
    app.add_handler(CommandHandler("add_note", add_note))
    app.add_handler(CommandHandler("goals", goals))
    app.add_handler(CommandHandler("notes", notes))
    app.add_handler(CommandHandler("deadlines", deadlines))

    # Обработчик всех текстовых сообщений (для кода привязки)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print(" Telegram-бот запущен. Ожидаю команды /start или код привязки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_telegram_bot()