import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from google.cloud import storage

from .models import Photo

User = get_user_model()

@csrf_exempt  # 外部(GCF)から叩かれるのでCSRF無効化
@require_POST
def photo_api(request):
    """
    Cloud Function からPOSTされる写真メタデータを受け取り、Photoを作成。
    最新画像を更新する際に gcs_id を返す。
    """
    try:
        data = json.loads(request.body)
        owner_id = data["owner_id"]
        bucket = data["bucket"]
        name = data["name"]
        size = data["size"]
        content_type = data.get("content_type", "image/jpeg")
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({"error": f"Invalid payload: {e}"}, status=400)

    try:
        owner = User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # gcs_path と gcs_id を生成
    gcs_path = f"gs://{bucket}/{name}"
    gcs_id = name.split(".")[0]  # 例: photo_20250921_103045_1

    photo = Photo.objects.create(
        owner=owner,
        gcs_path=gcs_path,
        size=size,
        content_type=content_type,
        gcs_id=gcs_id
    )

    return JsonResponse({
        "status": "success",
        "photo_id": photo.id,
        "gcs_id": photo.gcs_id
    })

@login_required
def photo_serve(request):
    """
    gcs_id で最新画像または任意の画像を取得する
    ?id=<gcs_id> で指定可能
    """
    gcs_id = request.GET.get("id")

    if gcs_id:
        photo = get_object_or_404(Photo, gcs_id=gcs_id)
    else:
        # 最新の写真1件
        photo = Photo.objects.filter(owner=request.user).order_by("-uploaded_at").first()
        if not photo:
            return HttpResponseForbidden("No photo available")

    # 所有者チェック
    if photo.owner != request.user:
        return HttpResponseForbidden("You do not have permission to access this photo.")

    # GCS から読み込み
    client = storage.Client()
    bucket_name, blob_name = photo.gcs_path.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    stream = blob.open("rb")

    response = FileResponse(stream, content_type=photo.content_type)
    # response["Content-Length"] = photo.size
    return response