# Create your tests here.
# dashboard/test.py
import os
import sys
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
#подключение многопоточности в тестах
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cortex.settings')
from django.conf import settings
settings.DATABASES['default']['OPTIONS'] = {'check_same_thread': False}
# добавляем dashboard в путь, чтобы импортировать telegram_bot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .models import Goal, Note, Deadline, TelegramProfile
import telegram_bot
from asgiref.sync import async_to_sync
#ТЕСТЫ МОДЕЛЕЙ

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

    def test_goal_creation(self):
        goal = Goal.objects.create(user=self.user, title='Изучить Docker')
        self.assertEqual(goal.title, 'Изучить Docker')
        self.assertEqual(goal.user, self.user)
        self.assertEqual(str(goal), 'Изучить Docker')

    def test_note_creation(self):
        note = Note.objects.create(user=self.user, title='Заметка о боте')
        self.assertEqual(note.title, 'Заметка о боте')
        self.assertEqual(note.user, self.user)
        self.assertEqual(str(note), 'Заметка о боте')

    def test_deadline_creation(self):
        from datetime import datetime
        from django.utils import timezone #для устранения ошиьки с наивной датой
        deadline = Deadline.objects.create(
            user=self.user,
            title='Срок сдачи',
            due_date=timezone.make_aware(datetime(2025, 12, 25, 15, 0))
        )
        self.assertEqual(deadline.title, 'Срок сдачи')

    def test_telegram_profile_uniqueness(self):
        TelegramProfile.objects.create(user=self.user, telegram_id='123456789')
        with self.assertRaises(Exception):
            TelegramProfile.objects.create(user=self.user, telegram_id='123456789')

#ТЕСТЫ ВЕБ

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secure123')
        self.client = Client()
        self.client.login(username='testuser', password='secure123')

    def test_goal_list_view(self):
        Goal.objects.create(user=self.user, title='Цель 1')
        response = self.client.get(reverse('dashboard:goal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Цель 1')

    def test_goal_create_view(self):
        response = self.client.post(reverse('dashboard:goal_create'), {'title': 'Новая цель'})
        self.assertRedirects(response, reverse('dashboard:goal_list'))
        self.assertTrue(Goal.objects.filter(title='Новая цель').exists())

    def test_note_list_view(self):
        Note.objects.create(user=self.user, title='Заметка 1')
        response = self.client.get(reverse('dashboard:note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заметка 1')

    def test_note_create_view(self):
        response = self.client.post(reverse('dashboard:note_create'), {'title': 'Новая заметка'})
        self.assertRedirects(response, reverse('dashboard:note_list'))
        self.assertTrue(Note.objects.filter(title='Новая заметка').exists())

#ТЕСТЫ TELEGRAM-БОТА

class MockUser:
    def __init__(self, id, username=None):
        self.id = id
        self.username = username


class MockMessage:
    def __init__(self):
        self.reply_text_content = ""

    async def reply_text(self, text):
        self.reply_text_content = text


class MockUpdate:
    def __init__(self, user_id, username=None, message_text=""):
        self.effective_user = MockUser(user_id, username)
        self.message = MockMessage()


class MockContext:
    def __init__(self, args=None):
        self.args = args or []


class TelegramBotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='telegram_user')
        TelegramProfile.objects.create(user=self.user, telegram_id='987654321')

    def test_get_user_by_telegram_id_success(self):
        #превращение асинхронной функции в синхронную
        get_user_sync = async_to_sync(telegram_bot.get_user_by_telegram_id)
        user = get_user_sync('987654321')
        self.assertEqual(user.username, 'telegram_user')

    def test_get_user_by_telegram_id_not_found(self):
        get_user_sync = async_to_sync(telegram_bot.get_user_by_telegram_id)
        user = get_user_sync('000000000')
        self.assertIsNone(user)

    def test_add_goal_saves_to_db(self):
        #проверяем, что цель создаётся
        Goal.objects.create(user=self.user, title='Тест из бота')
        self.assertTrue(Goal.objects.filter(title='Тест из бота').exists())