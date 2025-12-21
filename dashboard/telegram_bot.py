# dashboard/telegram_bot.py
import os
import sys
import django
from asgiref.sync import sync_to_async  # ← новое
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cortex.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import Note, Deadline, Goal, TelegramProfile
from django.db import IntegrityError
# Обёртки для синхронных Django-вызовов
@sync_to_async
def get_first_user():
    return User.objects.first()

@sync_to_async
def get_user_notes(user):
    return list(Note.objects.filter(user=user))

@sync_to_async
def get_user_goals(user):
    return list(Goal.objects.filter(user=user))


@sync_to_async
def get_user_deadlines(user):
    return list(Deadline.objects.filter(user=user))

@sync_to_async
def create_user_and_profile(username, user_id):
    from django.contrib.auth.models import User
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f"{username}@cortex.local"}
    )
    user.set_unusable_password()
    user.save()

    try:
        TelegramProfile.objects.create(user=user, telegram_id=user_id)
        return user, True
    except IntegrityError:
        return user, False

@sync_to_async
def add_goal_to_db(user, title):
    return Goal.objects.create(user=user, title=title)

@sync_to_async
def add_note_to_db(user, title):
    return Note.objects.create(user=user, title=title)

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        profile = TelegramProfile.objects.get(telegram_id=telegram_id)
        return profile.user
    except TelegramProfile.DoesNotExist:
        return None

@sync_to_async
def get_all_user_data(user):
    return {
        'goals': list(Goal.objects.filter(user=user)),
        'notes': list(Note.objects.filter(user=user)),
        'deadlines': list(Deadline.objects.filter(user=user)),
    }

# Асинхронные обработчики
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_first_user()
    if user:
        notes_list = await get_user_notes(user)
        text = "Ваши заметки:\n" + "\n".join(f"- {n.title}" for n in notes_list) if notes_list else "Нет заметок."
    else:
        text = "Нет пользователей."
    await update.message.reply_text(text)

async def deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_first_user()
    if user:
        deadlines_list = await get_user_deadlines(user)
        text = "Ваши дедлайны:\n" + "\n".join(
            f"- {d.title} ({d.due_date.strftime('%d.%m.%Y %H:%M')})" for d in deadlines_list
        ) if deadlines_list else "Нет дедлайнов."
    else:
        text = "Нет пользователей."
    await update.message.reply_text(text)

async def goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_first_user()
    if user:
        goals_list = await get_user_goals(user)
        text = "Ваши цели:\n" + "\n".join(f"- {g.title}" for g in goals_list) if goals_list else "Нет целей."
    else:
        text = "Нет пользователей."
    await update.message.reply_text(text)

#Команда :/start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = await get_user_by_telegram_id(user_id)

    #привязка телеграмм id
    if user:
        await update.message.reply_text("Вы подключены к Cortex!")
    else:
        await update.message.reply_text(
            "Ваш Telegram ID не привязан к учетной записи.\n"
            "Свяжитесь с админом для привязки"
        )

#команда: /add_goal <текст>
async def add_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    goal_text = " ".join(context.args)

    if not goal_text:
        await update.message.reply_text("Использование: /add_goal Название цели")
        return

    user = await get_user_by_telegram_id(user_id)
    if not user:
        await update.message.reply_text("Вы не подключены! Для начала отправьте команду: /start")
        return

    await add_goal_to_db(user, goal_text)
    await update.message.reply_text(f"Цель '{goal_text}' добавлена!")

# команда: /add_note <текст>
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    note_text = " ".join(context.args)

    if not note_text:
        await update.message.reply_text("Использование: /add_note Название заметки")
        return

    user = await get_user_by_telegram_id(user_id)
    if not user:
        await update.message.reply_text("Вы не подключены! Для начала отправьте команду: /start")
        return

    await add_note_to_db(user, note_text)
    await update.message.reply_text(f"Заметка '{note_text}' добавлена!")

#Команда: /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = await get_user_by_telegram_id(user_id)

    if not user:
        await update.message.reply_text("Использование: /add_note Название заметки")
        return

    data = await get_all_user_data(user)

    goals_text = "\n".join(f"- {g.title}" for g in data['goals']) or "Нет целей."
    notes_text = "\n".join(f"- {n.title}" for n in data['notes']) or "Нет заметок."
    deadlines_text = "\n".join(f"- {d.title} ({d.due_date.strftime('%d.%m.%Y %H:%M')})" for d in data['deadlines']) or "Нет дедлайнов."

    text = f"""
Ващи текущие данные в Cortex:
ЦЕЛИ:
{goals_text}
ЗАМЕТКИ:
{notes_text}
ДЕДЛАЙНЫ:
{deadlines_text}
        """
    await update.message.reply_text(text)

# Функция запуска
def run_telegram_bot():
    from django.conf import settings
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("notes", notes))
    app.add_handler(CommandHandler("deadlines", deadlines))
    app.add_handler(CommandHandler("goals", goals))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("add_goal", add_goal))
    app.add_handler(CommandHandler("add_note", add_note))
    print("Бот запущен! Напишите /start в Telegram.")
    app.run_polling()
if __name__ == "__main__":
    run_telegram_bot()

