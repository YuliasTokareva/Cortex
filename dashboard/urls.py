from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/new/', views.goal_create, name='goal_create'),
]