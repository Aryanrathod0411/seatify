from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('add/', views.add_room, name='add_room'),
    path('<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('<int:room_id>/delete/', views.delete_room, name='delete_room'),
]