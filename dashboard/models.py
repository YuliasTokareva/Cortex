from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name="Ваша цель")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(blank=True, verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Заметка"
        verbose_name_plural = "Заметки"


class Deadline(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    due_date = models.DateTimeField(verbose_name="Дата и время дедлайна")
    completed = models.BooleanField(default=False, verbose_name="Выполнено")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Дедлайн"
        verbose_name_plural = "Дедлайны"
        ordering = ['due_date']


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"({self.user.username}={self.telegram_id})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    binding_code = models.CharField(max_length=12, unique=True, blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Используем get_or_create, чтобы избежать дублей
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'binding_code': secrets.token_urlsafe(8)}
        )