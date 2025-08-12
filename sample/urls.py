from django.urls import path, include
from . import views

app_name = 'sample'

urlpatterns = [
    path('', views.home, name='home'),
]
