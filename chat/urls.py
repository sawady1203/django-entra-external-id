from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),  # Include the chat app URLs
    path('room/<str:room_name>/<str:username>/', views.chatroom, name='chatroom'),
]
