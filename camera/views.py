# camera/views.py
import os
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils.gcf import invoke_take_picture_function

from photo.models import Photo


@login_required
def camera_home(request):
    """
    カメラホームページ
    最新の写真を取得してテンプレートに渡す
    """
    latest_photo = (
        Photo.objects.filter(owner=request.user)
        .order_by("-uploaded_at")
        .first()
    )
    return render(request, "camera/home.html", {"latest_photo": latest_photo})


PHOTO_CREATION_WAIT_SECONDS = int(os.environ.get("PHOTO_CREATION_WAIT_SECONDS", 7))

@login_required
@csrf_exempt
def take_picture(request):
    """
    撮影依頼を送信 → 少し待機 → 最新画像を返す
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "invalid method"}, status=400)

    try:
        # Cloud Function へ撮影指示 (Pub/Sub)
        data = invoke_take_picture_function(request.user)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # 少し待機して Cloud Function が Photo レコードを作成するのを待つ
    time.sleep(PHOTO_CREATION_WAIT_SECONDS)

    # 最新 Photo を取得（DB は1回だけ）
    latest_photo = Photo.objects.filter(owner=request.user).order_by("-uploaded_at").first()

    if not latest_photo:
        return JsonResponse({"status": "error", "message": "最新画像情報が取得できませんでした"})

    return JsonResponse({
        "status": "success",
        "gcs_id": latest_photo.gcs_id,
        "message": "撮影完了"
    })