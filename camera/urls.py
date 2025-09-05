from django.urls import path
from . import views

app_name = "camera"

urlpatterns = [
    path('', views.camera_home, name='camera_home'),
    path("api/take-picture/", views.take_picture, name="take_picture"),
]
