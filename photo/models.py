from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

class Photo(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="photos",
    )
    gcs_path = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("photo:photo_serve", args=[self.id])

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.owner} - {self.gcs_path}"
