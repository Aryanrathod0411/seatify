from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render

def faculty_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('admin_panel')

        return render(
            request,
            'accounts/faculty_login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(
        request,
        'accounts/faculty_login.html'
    )
from django.utils import timezone

from django.utils import timezone


@login_required
def admin_panel(request):

    from students.models import Student
    from exams.models import Exam
    from rooms.models import Room
    from seating.models import Seating

    today = timezone.localdate()
    upcoming_exams = Exam.objects.filter(
        exam_date__gte=today
    ).order_by(
        'exam_date',
        'start_time'
    )
    generated_exam_ids = Seating.objects.values_list(
        'exam_id',
        flat=True
    ).distinct()
    context = {
        'today': today,
        'student_count': Student.objects.count(),
        'exam_count': upcoming_exams.count(),
        'room_count': Room.objects.count(),
        'seat_count': Seating.objects.filter(
            exam__exam_date__gte=today
        ).count(),
        'pending_exam_count': upcoming_exams.exclude(
            id__in=generated_exam_ids
        ).count(),
        'recent_exams': upcoming_exams[:6],
    }

    return render(
        request,
        'accounts/admin_panel.html',
        context
    )


@login_required
def faculty_dashboard(request):
    return redirect('admin_panel')


def faculty_logout(request):
    logout(request)
    return redirect('/faculty/login/')

def home(request):
    return render(request, 'accounts/home.html')