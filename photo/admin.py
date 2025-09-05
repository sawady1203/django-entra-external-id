from django.contrib import admin

# Register your models here.
from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "name", "uploaded_at")
    search_fields = ("name",)
    list_filter = ("owner",)