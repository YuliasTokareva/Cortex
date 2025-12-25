from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.dashboard_main, name='main'),
    # Цели Юля
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/new/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_update, name='goal_update'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),

    # Заметки Даша
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('notes/new/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    # Дедлайны Даша
    path('deadlines/', views.DeadlineListView.as_view(), name='deadline_list'),
    path('deadlines/new/', views.DeadlineCreateView.as_view(), name='deadline_create'),
    path('deadlines/<int:pk>/edit/', views.DeadlineUpdateView.as_view(), name='deadline_update'),
    path('deadlines/<int:pk>/delete/', views.DeadlineDeleteView.as_view(), name='deadline_delete'),

    # для телеграмм бота
    path('start-bot/', views.start_telegram_bot, name='start_bot'),
]
