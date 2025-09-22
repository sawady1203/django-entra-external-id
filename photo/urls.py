# photo/urls.py
from django.urls import path
from . import views

app_name = "photo"

urlpatterns = [
    path("api/", views.photo_api, name="photo_api"),
    path("serve/", views.photo_serve, name="photo_serve"),  # 最新1件
    path("serve/<uuid:gcs_id>/", views.photo_serve, name="photo_serve_by_gcs"),
    path("serve/latest/", views.latest_photo_api, name="latest_photo_api"),  # 最新1件
]
