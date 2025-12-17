# dashboard/telegram_bot.py
import os
import django
from asgiref.sync import sync_to_async  # ← новое
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cortex.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import Note, Deadline

# Обёртки для синхронных Django-вызовов
@sync_to_async
def get_first_user():
    return User.objects.first()

@sync_to_async
def get_user_notes(user):
    return list(Note.objects.filter(user=user))

@sync_to_async
def get_user_deadlines(user):
    return list(Deadline.objects.filter(user=user))

# Асинхронные обработчики
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_first_user()
    if user:
        notes_list = await get_user_notes(user)
        text = "📝 Ваши заметки:\n" + "\n".join(f"- {n.title}" for n in notes_list) if notes_list else "Нет заметок."
    else:
        text = "Нет пользователей."
    await update.message.reply_text(text)

async def deadlines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_first_user()
    if user:
        deadlines_list = await get_user_deadlines(user)
        text = "⏰ Ваши дедлайны:\n" + "\n".join(
            f"- {d.title} ({d.due_date.strftime('%d.%m.%Y %H:%M')})" for d in deadlines_list
        ) if deadlines_list else "Нет дедлайнов."
    else:
        text = "Нет пользователей."
    await update.message.reply_text(text)

# Функция запуска
def run_telegram_bot():
    from django.conf import settings
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("notes", notes))
    app.add_handler(CommandHandler("deadlines", deadlines))
    return app