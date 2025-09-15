from django.shortcuts import render, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils.gcf import invoke_take_picture_function

from photo.models import Photo

@login_required
def camera_home(request):
    latest_photo = Photo.objects.filter(owner=request.user).first()
    return render(request, "camera/home.html", {"latest_photo": latest_photo})

@login_required
@csrf_exempt
def take_picture(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=400)

    # body = json.loads(request.body)
    # group_id = body.get("group_id")

    # if group_id not in request.user.groups.values_list("id", flat=True):
    #     return JsonResponse({"error": "invalid group"}, status=403)

    text, status = invoke_take_picture_function(request.user)
     # 撮影依頼後 → camera_home にリダイレクト
    return HttpResponseRedirect(reverse("camera:camera_home"))
