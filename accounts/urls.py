from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.faculty_login, name='faculty_login'),
    path('dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
]