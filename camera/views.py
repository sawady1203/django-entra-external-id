# camera/views.py
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


@login_required
@csrf_exempt
def take_picture(request):
    """
    撮影依頼を送信する Ajax 用ビュー
    JSON でレスポンスを返す
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "invalid method"}, status=400)

    try:
        data = invoke_take_picture_function(request.user)  # Cloud Function 呼び出し
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Cloud Function が GCS に保存したあとに Django API (photo_api) が Photo レコードを作成する想定
    # 最新 Photo を取得して gcs_id を返す
    from photo.models import Photo
    import time

    latest_photo = None
    for _ in range(10):  # 最大 10 回リトライ（GCS → Django の Photo 作成待ち）
        latest_photo = Photo.objects.filter(owner=request.user).order_by("-uploaded_at").first()
        if latest_photo:
            break
        time.sleep(0.5)  # 500ms 待つ

    if not latest_photo:
        return JsonResponse({"status": "error", "message": "最新画像情報が取得できませんでした"})

    return JsonResponse({
        "status": "success",
        "gcs_id": latest_photo.gcs_id,
        "message": "撮影完了"
    })
