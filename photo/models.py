from django.db import models
from django.contrib.auth import get_user_model


class Photo(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="photos",
        help_text="この写真を所有するユーザー"
    )
    bucket = models.CharField(max_length=255, help_text="保存先のGCSバケット名")
    name = models.CharField(max_length=1024, help_text="GCSオブジェクトのパス")
    size = models.BigIntegerField(help_text="ファイルサイズ (バイト)")
    content_type = models.CharField(max_length=100, help_text="MIMEタイプ (例: image/jpeg)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"

    class Meta:
        app_label = "photo"
        ordering = ["-uploaded_at"]
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
