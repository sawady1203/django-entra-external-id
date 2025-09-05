import json
from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.cloud import storage
from .models import Photo
from .sse import notify_photo_created  # 後述

DJANGO_AUDIENCE = "https://django-entra-external-id.vercel.app/photo/api/"  # Cloud Functionsで使ったURL

@csrf_exempt
def photo_create_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return HttpResponseForbidden("Missing Bearer token")
    token = auth_header.split(" ", 1)[1]

    try:
        claims = id_token.verify_oauth2_token(token, google_requests.Request(), DJANGO_AUDIENCE)
        # claims['sub'] や claims['email'] でユーザー確認可能
    except Exception:
        return HttpResponseForbidden("Invalid token")

    try:
        data = json.loads(request.body)
        owner_id = data["owner_id"]
        bucket = data["bucket"]
        name = data["name"]
        size = data["size"]
        content_type = data.get("content_type", "image/jpeg")
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid payload"}, status=400)

    User = get_user_model()
    try:
        owner = User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    photo = Photo.objects.create(
        owner=owner,
        bucket=bucket,
        name=name,
        size=size,
        content_type=content_type,
    )

    notify_photo_created(photo)

    return JsonResponse({"status": "ok", "photo_id": photo.id})


@login_required
def photo_serve(request, photo_id):
    """
    認証済みユーザーのみが写真を取得できる。
    GCS から直接読み込み、レスポンスで返す。
    """
    photo = get_object_or_404(Photo, id=photo_id)

    # 所有者のみアクセス可能
    if photo.owner != request.user:
        return HttpResponseForbidden("You do not have permission to access this photo.")

    # GCS クライアント
    client = storage.Client()
    bucket = client.bucket(photo.bucket)
    blob = bucket.blob(photo.name)

    # Blob を読み込みバイト列として返す
    stream = blob.open("rb")  # read-binary モード
    response = FileResponse(stream, content_type=photo.content_type)
    response["Content-Length"] = photo.size
    return response


from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
import time

@login_required
def photo_stream(request):
    def event_stream():
        last_id = 0
        while True:
            photos = Photo.objects.filter(owner=request.user, id__gt=last_id).order_by("id")
            for photo in photos:
                yield f"data: {json.dumps({'photo_id': photo.id})}\n\n"
                last_id = photo.id
            time.sleep(1)  # 1秒ごとにチェック

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
