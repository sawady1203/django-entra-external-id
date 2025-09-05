from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Render the home page.
    """
    return render(request, 'sample/home.html')

@login_required
def required(request):
    """
    Render the required page.
    """
    return render(request, 'sample/required.html')