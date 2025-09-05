from django.urls import path
from . import views

app_name = "photo"

urlpatterns = [
    path("api/", views.photo_create_api, name="photo_create_api"),
    path("stream/", views.photo_stream, name="photo_stream"),
]

urlpatterns += [
    path("media/<int:photo_id>/", views.photo_serve, name="photo_serve"),
]
