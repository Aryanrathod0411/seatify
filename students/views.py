from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Student
from seating.models import Seating
from exams.models import Exam
import pandas as pd
from .forms import StudentForm


@login_required
def add_student(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('student_list')
    return render(
        request,
        'students/add_student.html',
        {'form': form}
    )


@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('student_list')
    return render(
        request,
        'students/add_student.html',
        {'form': form, 'student': student}
    )


@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(
        request,
        'accounts/confirm_delete.html',
        {
            'object': student,
            'object_type': 'student record',
            'seating_count': Seating.objects.filter(student=student).count(),
            'cancel_url': '/students/',
        }
    )


@login_required
def student_list(request):

    search = request.GET.get('search', '')
    selected_branch = request.GET.get('branch', '')

    # Sabhi branches nikalo
    branches = (
        Student.objects
        .values_list('branch', flat=True)
        .distinct()
        .order_by('branch')
    )

    # Students
    students = Student.objects.all()

    # Branch filter
    if selected_branch:
        students = students.filter(
            branch=selected_branch
        )

    # Search filter
    if search:
        students = students.filter(
            name__icontains=search
        ) | students.filter(
            enrollment_number__icontains=search
        )

    return render(
        request,
        'students/student_list.html',
        {
            'students': students,
            'search': search,
            'branches': branches,
            'selected_branch': selected_branch,
        }
    )



@login_required
def upload_students(request):

    if request.method == 'POST':

        file = request.FILES.get('student_file')

        if file:

            file_name = file.name.lower()

            # CSV file
            if file_name.endswith('.csv'):
                df = pd.read_csv(file)

            # Excel file
            elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                df = pd.read_excel(file)

            else:
                return render(
                    request,
                    'students/upload_students.html',
                    {
                        'error': 'Please upload a CSV or Excel file.'
                    }
                )

            # Column names clean karo
            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            # Required columns check
            required_columns = [
                'Name',
                'Roll Number',
                'Enrollment Number',
                'Branch',
                'Semester',
                'Email'
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                return render(
                    request,
                    'students/upload_students.html',
                    {
                        'error': (
                            'Missing columns: '
                            + ', '.join(missing_columns)
                        )
                    }
                )

            # Students database me save karo
            for _, row in df.iterrows():

                Student.objects.create(
                    name=str(row['Name']).strip(),

                    roll_number=str(
                        row['Roll Number']
                    ).strip(),

                    enrollment_number=str(
                        row['Enrollment Number']
                    ).strip(),

                    branch=str(
                        row['Branch']
                    ).strip(),

                    semester=int(
                        row['Semester']
                    ),

                    email=str(
                        row['Email']
                    ).strip()
                )

    return render(
        request,
        'students/upload_students.html'
    )

def student_seat(request):

    seating = None
    enrollment_number = ''
    exam_id = ''

    # Sirf wahi exams jinka seating generate ho chuka hai
    generated_exam_ids = (
        Seating.objects
        .values_list('exam_id', flat=True)
        .distinct()
    )

    exams = (
        Exam.objects
        .filter(id__in=generated_exam_ids)
        .order_by('-exam_date', '-start_time')
    )

    if request.method == 'POST':

        enrollment_number = request.POST.get('enrollment_number', '').strip()
        exam_id = request.POST.get('exam_id')

        student = Student.objects.filter(
            enrollment_number=enrollment_number
        ).first()

        if student and exam_id:

            seating = Seating.objects.filter(
                student=student,
                exam_id=exam_id
            ).select_related(
                'student',
                'room',
                'exam'
            ).first()

    return render(
        request,
        'students/student_seat.html',
        {
            'seating': seating,
            'enrollment_number': enrollment_number,
            'exam_id': exam_id,
            'exams': exams,
        }
    )