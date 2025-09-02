from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils.gcf import invoke_take_picture_function

def camera_home(request):
    return render(request, "camera/home.html")

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
    return JsonResponse({"message": text}, status=status)
