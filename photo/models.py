from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

class Photo(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="photos",
        help_text="この写真を所有するユーザー"
    )
    gcs_path = models.CharField(
        max_length=1024, 
        default="",
        help_text="GCSオブジェクトのフルパス (例: gs://bucket/name)")
    size = models.BigIntegerField(default=0, help_text="ファイルサイズ (バイト)")
    content_type = models.CharField(max_length=100, default="image/jpeg", help_text="MIMEタイプ (例: image/jpeg)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gcs_path} ({self.owner})"

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
