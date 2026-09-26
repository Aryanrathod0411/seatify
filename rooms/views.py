from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room
from seating.models import Seating
from .forms import RoomForm


@login_required
def room_list(request):

    rooms = Room.objects.all()

    return render(
        request,
        'rooms/room_list.html',
        {
            'rooms': rooms
        }
    )


@login_required
def add_room(request):
    form = RoomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('room_list')
    return render(
        request,
        'rooms/add_room.html',
        {'form': form}
    )


@login_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('room_list')
    return render(
        request,
        'rooms/add_room.html',
        {'form': form, 'room': room}
    )


@login_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        room.delete()
        return redirect('room_list')
    return render(
        request,
        'accounts/confirm_delete.html',
        {
            'object': room,
            'object_type': 'room',
            'seating_count': Seating.objects.filter(room=room).count(),
            'cancel_url': '/rooms/',
        }
    )