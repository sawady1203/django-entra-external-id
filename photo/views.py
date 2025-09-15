from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Photo

@login_required
def latest_photo(request):
    photo = Photo.objects.filter(owner=request.user).first()
    return render(request, "photo/latest.html", {"photo": photo})

@login_required
def photo_latest_api(request):
    """ログインユーザーの最新の写真を返すAPI"""
    latest_photo = Photo.objects.filter(owner=request.user).first()
    if not latest_photo:
        return JsonResponse({"error": "no photo"}, status=404)

    return JsonResponse({
        "id": latest_photo.id,
        "url": request.build_absolute_uri(
            latest_photo.get_absolute_url()  # もし model に実装してなければ photo_serve を逆引き
        )
    })
