import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cortex.settings')
django.setup()

from dashboard.telegram_bot import run_telegram_bot

if __name__ == '__main__':
    app = run_telegram_bot()
    print("Telegram бот запущен...")
    app.run_polling(drop_pending_updates=True)