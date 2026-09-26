from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', views.admin_panel, name='admin_panel'),
    path('', views.home, name='home'),
    path('students/', include('students.urls')),
    path('seating/', include('seating.urls')),
    path('faculty/', include('accounts.urls')),
    path('exams/', include('exams.urls')),
    path('rooms/', include('rooms.urls')),
]
