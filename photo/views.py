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
    try:
        data = json.loads(request.body)
        owner_id = data["owner_id"]
        bucket = data["bucket"]
        name = data["name"]
        size = data["size"]
        content_type = data.get("content_type", "image/jpeg")
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({"error": f"Invalid payload: {e}"}, status=400)

    User = get_user_model()
    try:
        owner = User.objects.get(id=owner_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    gcs_path = f"gs://{bucket}/{name}"

    photo = Photo.objects.create(
        owner=owner,
        gcs_path=gcs_path,
        size=size,
        content_type=content_type,
    )

    return JsonResponse({"status": "created", "photo_id": photo.id})


@login_required
def photo_serve(request, photo_id=None):
    if photo_id:
        photo = get_object_or_404(Photo, id=photo_id)
    else:
        photo = Photo.objects.filter(owner=request.user).order_by("-uploaded_at").first()

    if not photo or photo.owner != request.user:
        return HttpResponseForbidden("You do not have permission to access this photo.")

    # gcs_path から bucket と object を取得
    bucket_name, blob_name = parse_gcs_path(photo.gcs_path)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    stream = blob.open("rb")

    response = FileResponse(stream, content_type=photo.content_type)
    response["Content-Length"] = photo.size
    return response

def parse_gcs_path(gcs_path: str):
    # gs://bucket_name/object_name -> ("bucket_name", "object_name")
    if not gcs_path.startswith("gs://"):
        raise ValueError("Invalid gcs_path")
    path = gcs_path[5:]  # "bucket_name/object_name"
    bucket_name, blob_name = path.split("/", 1)
    return bucket_name, blob_name
