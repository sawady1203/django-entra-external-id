from django.shortcuts import render

# Create your views here.

def index(request):

    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        username = request.POST.get('username')
        # Handle the form submission, e.g., create or join a chat room
        # For now, we'll just render the same page with the room name and username
        print(f"Room Name: {room_name}, Username: {username}")

    return render(request, 'chat/index.html')


def chatroom(request, room_name, username):
    context = {
        'room_name': room_name,
        'username': username
    }

    return render(request, 'chat/room.html', context)