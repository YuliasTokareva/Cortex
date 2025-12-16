from django.db import models
from django.contrib.auth.models import User
# Create your models here.
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