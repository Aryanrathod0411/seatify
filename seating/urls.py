from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_seating, name='generate_seating'),
    path('map/', views.seat_map, name='seat_map'),
    path('export-excel/', views.export_seating_excel, name='export_seating_excel'),
]