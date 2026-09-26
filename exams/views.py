from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Exam, TimetableUpload
import pandas as pd

from students.models import Student
from seating.models import Seating
from .forms import ExamForm


# =========================================================
# EXAM LIST
# =========================================================

@login_required
def exam_list(request):

    today = timezone.localdate()

    # ---------------------------------------
    # UPDATE EXAM STATUS AUTOMATICALLY
    # ---------------------------------------

    all_exams = Exam.objects.all()

    for exam in all_exams:

        if exam.exam_date < today:

            if exam.status != 'Completed':
                exam.status = 'Completed'
                exam.save(update_fields=['status'])

        elif exam.exam_date == today:

            if exam.status != 'Ongoing':
                exam.status = 'Ongoing'
                exam.save(update_fields=['status'])

        else:

            if exam.status != 'Upcoming':
                exam.status = 'Upcoming'
                exam.save(update_fields=['status'])

    # ---------------------------------------
    # UPCOMING + TODAY EXAMS
    # ---------------------------------------

    upcoming_exams = (
        Exam.objects
        .filter(exam_date__gte=today)
        .order_by('exam_date', 'start_time')
    )

    # ---------------------------------------
    # PAST EXAMS
    # ---------------------------------------

    past_exams = (
        Exam.objects
        .filter(exam_date__lt=today)
        .order_by('-exam_date', '-start_time')
    )

    return render(
        request,
        'exams/exam_list.html',
        {
            'exams': upcoming_exams,
            'upcoming_exams': upcoming_exams,
            'past_exams': past_exams,
            'today': today,
        }
    )


# =========================================================
# ADD EXAM
# =========================================================
@login_required
def add_exam(request):
    form = ExamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('exam_list')
    return render(
        request,
        'exams/add_exam.html',
        {'form': form}
    )


@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    form = ExamForm(request.POST or None, instance=exam)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('exam_list')
    return render(
        request,
        'exams/add_exam.html',
        {'form': form, 'exam': exam}
    )


@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam_list')
    return render(
        request,
        'accounts/confirm_delete.html',
        {
            'object': exam,
            'object_type': 'exam',
            'seating_count': Seating.objects.filter(exam=exam).count(),
            'cancel_url': '/exams/',
        }
    )


# =========================================================
# UPLOAD TIMETABLE
# =========================================================

@login_required
def upload_timetable(request):

    if request.method == 'POST':

        file = request.FILES.get(
            'timetable_file'
        )

        if file:

            TimetableUpload.objects.create(
                file=file
            )

            df = pd.read_excel(
                file,
                header=6
            )

            # ---------------------------------------
            # MERGED CELLS
            # ---------------------------------------

            df['Branch'] = df['Branch'].ffill()
            df['Semester'] = df['Semester'].ffill()
            df['Date'] = df['Date'].ffill()

            # ---------------------------------------
            # READ EACH EXAM
            # ---------------------------------------

            for _, row in df.iterrows():

                exam_code = str(
                    row['Exam Code']
                ).strip()

                subject = str(
                    row['Subject']
                ).strip()

                branch = str(
                    row['Branch']
                ).strip()

                # -----------------------------------
                # BASIC CHECK
                # -----------------------------------

                if not exam_code or exam_code == 'nan':
                    continue

                if not subject or subject == 'nan':
                    continue

                # -----------------------------------
                # DATE
                # -----------------------------------

                exam_date = pd.to_datetime(
                    row['Date'],
                    dayfirst=True,
                    errors='coerce'
                )

                if pd.isna(exam_date):
                    continue

                exam_date = exam_date.date()

                # -----------------------------------
                # TIME
                # -----------------------------------

                time_value = row['Time']

                if pd.isna(time_value):
                    continue

                time_text = str(
                    time_value
                ).strip()

                if '-' not in time_text:
                    continue

                time_parts = time_text.split(
                    '-',
                    1
                )

                start_parsed = pd.to_datetime(
                    time_parts[0].strip(),
                    errors='coerce'
                )

                end_parsed = pd.to_datetime(
                    time_parts[1].strip(),
                    errors='coerce'
                )

                if (
                    pd.isna(start_parsed)
                    or pd.isna(end_parsed)
                ):
                    continue

                start_time = start_parsed.time()
                end_time = end_parsed.time()

                # -----------------------------------
                # SEMESTER
                # -----------------------------------

                semester_text = str(
                    row['Semester']
                ).strip().upper()

                semester_map = {
                    'I': 1,
                    'II': 2,
                    'III': 3,
                    'IV': 4,
                    'V': 5,
                    'VI': 6,
                    'VII': 7,
                    'VIII': 8
                }

                if semester_text in semester_map:

                    semester = semester_map[
                        semester_text
                    ]

                elif semester_text.isdigit():

                    semester = int(
                        semester_text
                    )

                else:

                    continue

                # -----------------------------------
                # CHECK EXISTING EXAM
                # -----------------------------------

                exam = Exam.objects.filter(
                    exam_name=exam_code,
                    subject=subject,
                    exam_date=exam_date
                ).first()

                # -----------------------------------
                # EXISTING EXAM
                # -----------------------------------

                if exam:

                    branches = exam.branches or []

                    if branch not in branches:

                        branches.append(
                            branch
                        )

                    exam.branches = branches

                    exam.save()

                # -----------------------------------
                # NEW EXAM
                # -----------------------------------

                else:

                    today = timezone.localdate()

                    if exam_date < today:

                        status = 'Completed'

                    elif exam_date == today:

                        status = 'Ongoing'

                    else:

                        status = 'Upcoming'

                    exam = Exam.objects.create(
                        exam_name=exam_code,
                        subject=subject,
                        semester=semester,
                        exam_date=exam_date,
                        start_time=start_time,
                        end_time=end_time,
                        status=status,
                        branches=[branch]
                    )

                # -----------------------------------
                # ADD STUDENTS
                # -----------------------------------

                students = Student.objects.filter(
                    semester=semester,
                    branch=branch
                )

                exam.students.add(
                    *students
                )

            return redirect(
                '/exams/'
            )

    return render(
        request,
        'exams/upload_timetable.html'
    )