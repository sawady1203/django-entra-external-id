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
    撮影依頼を送信し、Cloud Function のレスポンス (gcs_id) をそのまま返す
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "invalid method"}, status=400)

    try:
        data = invoke_take_picture_function(request.user)  # Cloud Function 呼び出し
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Cloud Function から gcs_id が返ってくる前提
    return JsonResponse(data)