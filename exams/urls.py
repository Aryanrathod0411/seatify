from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('add/', views.add_exam, name='add_exam'),
    path('<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('upload-timetable/', views.upload_timetable, name='upload_timetable'),
]