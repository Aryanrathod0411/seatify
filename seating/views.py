from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from students.models import Student
from .models import Seating
from exams.models import Exam
from rooms.models import Room
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.db import transaction
from django.utils import timezone


from django.shortcuts import render
from django.utils import timezone

from students.models import Student
from .models import Seating
from exams.models import Exam
from rooms.models import Room


@login_required
def seat_map(request):

    exam_id = request.GET.get('exam_id')
    room_id = request.GET.get('room_id')

    today = timezone.localdate()

    # Sirf future ya aaj ki exams
    # aur jin exams ki seating generate ho chuki hai
    generated_exam_ids = Seating.objects.values_list(
        'exam_id',
        flat=True
    ).distinct()

    exams = Exam.objects.filter(
        exam_date__gte=today,
        id__in=generated_exam_ids
    ).order_by(
        'exam_date',
        'start_time'
    )

    exam = None
    room = None
    rooms = []
    seatings = Seating.objects.none()

    # Exam select kiya
    if exam_id:

        exam = exams.filter(
            id=exam_id
        ).first()

        if exam:

            # Is exam ki seating jin rooms me hai
            room_ids = Seating.objects.filter(
                exam=exam
            ).values_list(
                'room_id',
                flat=True
            ).distinct()

            rooms = Room.objects.filter(
                id__in=room_ids
            )

            # Room select kiya
            if room_id:

                room = rooms.filter(
                    id=room_id
                ).first()

                if room:

                    seatings = Seating.objects.filter(
                        room=room,
                        exam=exam
                    ).select_related(
                        'student',
                        'room',
                        'exam'
                    )

    rows = []

    if room:

        for row_number in range(
            1,
            room.rows + 1
        ):

            tables = []

            for table_number in range(
                1,
                room.tables_per_row + 1
            ):

                seats = []

                for seat_number in range(
                    1,
                    room.seats_per_table + 1
                ):

                    seating = seatings.filter(
                        row_number=row_number,
                        table_number=table_number,
                        seat_number=seat_number
                    ).first()

                    seats.append({
                        'number': seat_number,
                        'seating': seating
                    })

                tables.append({
                    'number': table_number,
                    'seats': seats
                })

            rows.append({
                'number': row_number,
                'tables': tables
            })

    return render(
        request,
        'seating/seat_map.html',
        {
            'exams': exams,
            'exam': exam,
            'rooms': rooms,
            'room': room,
            'rows': rows,
        }
    )
    
from django.shortcuts import render
from students.models import Student
from .models import Seating
from exams.models import Exam
from rooms.models import Room
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.db import transaction
from django.utils import timezone


@login_required
def generate_seating(request):

    # ---------------------------------------
    # AVAILABLE EXAMS
    # ---------------------------------------

    def get_available_exams():

        today = timezone.localdate()

        generated_exam_ids = (
            Seating.objects
            .values_list(
                'exam_id',
                flat=True
            )
            .distinct()
        )

        return (
            Exam.objects
            .filter(
                exam_date__gte=today
            )
            .exclude(
                id__in=generated_exam_ids
            )
            .order_by(
                'exam_date',
                'start_time'
            )
        )

    # ---------------------------------------
    # INITIAL DATA
    # ---------------------------------------

    today = timezone.localdate()

    exams = (
        Exam.objects
        .filter(
            exam_date__gte=today
        )
        .order_by(
            'exam_date',
            'start_time'
        )
    )

    rooms = Room.objects.all()

    # ---------------------------------------
    # AVAILABLE BRANCHES
    # ---------------------------------------

    available_branches = (
        Student.objects
        .values_list(
            'branch',
            flat=True
        )
        .distinct()
        .order_by('branch')
    )

    # ---------------------------------------
    # POST REQUEST
    # ---------------------------------------

    if request.method == 'POST':

        exam_id = request.POST.get('exam_id')

        selected_branches = request.POST.getlist(
            'branches'
        )

        room_ids = request.POST.getlist(
            'room_ids'
        )

        # ---------------------------------------
        # BRANCH CHECK
        # ---------------------------------------

        if not selected_branches:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'Please select at least one branch.'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # EXAM CHECK
        # ---------------------------------------

        if not exam_id:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': 'Please select an exam.',
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # ROOM CHECK
        # ---------------------------------------

        if not room_ids:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'Please select at least one room.'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # GET EXAM
        # ---------------------------------------

        try:

            exam = Exam.objects.get(
                id=exam_id
            )

        except Exam.DoesNotExist:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'Selected exam does not exist.'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # PAST EXAM CHECK
        # ---------------------------------------

        if exam.exam_date < today:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'This exam date has already passed.'
                    ),
                    'exams': get_available_exams(),
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # ALREADY GENERATED CHECK
        # ---------------------------------------

        if Seating.objects.filter(
            exam=exam
        ).exists():

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'Seating has already been generated '
                        'for this exam.'
                    ),
                    'exams': get_available_exams(),
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # SELECTED ROOMS
        # ---------------------------------------

        selected_rooms = list(
            Room.objects.filter(
                id__in=room_ids
            )
        )

        # ---------------------------------------
        # ROOM SORTING
        # ---------------------------------------

        def room_sort_key(room):

            room_number = str(
                room.room_number
            ).strip()

            try:

                return (
                    0,
                    int(room_number)
                )

            except ValueError:

                return (
                    1,
                    room_number
                )

        selected_rooms.sort(
            key=room_sort_key
        )

        # ---------------------------------------
        # GET STUDENTS
        # ---------------------------------------

        students = list(
            Student.objects.filter(
                semester=exam.semester,
                branch__in=selected_branches
            )
        )

        # ---------------------------------------
        # ROLL NUMBER SORT
        # ---------------------------------------

        def roll_sort_key(student):

            roll = str(
                student.roll_number
            ).strip().upper()

            digits = ''

            for char in reversed(roll):

                if char.isdigit():

                    digits = char + digits

                else:

                    break

            if digits:

                prefix = roll[
                    :-len(digits)
                ]

                return (
                    prefix,
                    int(digits)
                )

            return (
                roll,
                0
            )

        students.sort(
            key=roll_sort_key
        )

        # ---------------------------------------
        # NO STUDENTS
        # ---------------------------------------

        if not students:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'No students found for the '
                        'selected branch(es).'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # GROUP STUDENTS BY BRANCH
        # ---------------------------------------

        students_by_branch = {}

        for student in students:

            if student.branch not in students_by_branch:

                students_by_branch[
                    student.branch
                ] = []

            students_by_branch[
                student.branch
            ].append(student)

        # ---------------------------------------
        # SORT EACH BRANCH
        # ---------------------------------------

        for branch in students_by_branch:

            students_by_branch[
                branch
            ].sort(
                key=roll_sort_key
            )

        # ---------------------------------------
        # ROOM CAPACITY CHECK
        # ---------------------------------------

        for room in selected_rooms:

            if room.seats_per_table < 2:

                return render(
                    request,
                    'seating/generate_seating.html',
                    {
                        'error': (
                            'Each table must have at least '
                            '2 seats.'
                        ),
                        'exams': exams,
                        'rooms': rooms,
                        'branches': available_branches,
                    }
                )

        # ---------------------------------------
        # EXISTING SEATING
        #
        # Same date + overlapping time
        # ---------------------------------------

        existing_seatings = (
            Seating.objects
            .filter(
                room__in=selected_rooms,
                exam__exam_date=exam.exam_date
            )
            .select_related(
                'student',
                'room',
                'exam'
            )
        )

        conflicting_seatings = []

        for seating in existing_seatings:

            old_exam = seating.exam

            # Time overlap check
            if (
                old_exam.start_time
                < exam.end_time
                and
                old_exam.end_time
                > exam.start_time
            ):

                conflicting_seatings.append(
                    seating
                )

        # ---------------------------------------
        # CREATE TABLE SLOTS
        # ---------------------------------------

        table_slots = []

        for room in selected_rooms:

            for row_number in range(
                1,
                room.rows + 1
            ):

                for table_number in range(
                    1,
                    room.tables_per_row + 1
                ):

                    occupied_seats = {}

                    occupied_branches = set()

                    # --------------------------------
                    # EXISTING OCCUPIED SEATS
                    # --------------------------------

                    for seating in conflicting_seatings:

                        if (
                            seating.room_id == room.id
                            and
                            seating.row_number == row_number
                            and
                            seating.table_number == table_number
                        ):

                            occupied_seats[
                                seating.seat_number
                            ] = seating.student

                            occupied_branches.add(
                                seating.student.branch
                            )

                    # --------------------------------
                    # EMPTY SEATS
                    # --------------------------------

                    available_seats = []

                    for seat_number in range(
                        1,
                        room.seats_per_table + 1
                    ):

                        if seat_number not in occupied_seats:

                            available_seats.append(
                                seat_number
                            )

                    # --------------------------------
                    # SAVE TABLE
                    # --------------------------------

                    if available_seats:

                        table_slots.append(
                            {
                                'room': room,
                                'row_number': row_number,
                                'table_number': table_number,
                                'available_seats': available_seats,
                                'occupied_branches': occupied_branches,
                            }
                        )

        # ---------------------------------------
        # NO EMPTY SEATS
        # ---------------------------------------

        if not table_slots:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        'No empty seats are available in '
                        'the selected rooms for this exam time.'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # FIND SINGLE SLOT
        # ---------------------------------------

        def find_single_slot(branch):

            for slot in table_slots:

                if not slot[
                    'available_seats'
                ]:

                    continue

                # Same branch cannot be at
                # same table.
                if branch in slot[
                    'occupied_branches'
                ]:

                    continue

                return slot

            return None

        # ---------------------------------------
        # FIND PAIR SLOT
        #
        # FIRST BRANCH  -> SEAT 1
        # SECOND BRANCH -> SEAT 2
        # ---------------------------------------

        def find_pair_slot(
            first_branch,
            second_branch
        ):

            for slot in table_slots:

                available_seats = slot[
                    'available_seats'
                ]

                occupied_branches = slot[
                    'occupied_branches'
                ]

                # Same branch already at table
                if first_branch in occupied_branches:

                    continue

                if second_branch in occupied_branches:

                    continue

                # First branch MUST get Seat 1
                if 1 not in available_seats:

                    continue

                # Second branch MUST get Seat 2
                if 2 not in available_seats:

                    continue

                return slot

            return None

        # ---------------------------------------
        # ASSIGNMENTS
        # ---------------------------------------

        assignments = []

        # ---------------------------------------
        # MAIN ALGORITHM
        # ---------------------------------------

        while True:

            # Only branches with students left
            branch_names = [
                branch
                for branch in students_by_branch
                if students_by_branch[branch]
            ]

            # All students assigned
            if not branch_names:

                break

            # Largest branch first
            branch_names.sort(
                key=lambda branch: len(
                    students_by_branch[branch]
                ),
                reverse=True
            )

            first_branch = branch_names[0]

            second_branch = None

            if len(branch_names) >= 2:

                second_branch = branch_names[1]

            # ---------------------------------------
            # TRY BRANCH PAIR
            # ---------------------------------------

            if second_branch:

                pair_slot = find_pair_slot(
                    first_branch,
                    second_branch
                )

                if pair_slot:

                    # --------------------------------
                    # FIRST BRANCH -> SEAT 1
                    # --------------------------------

                    student_1 = (
                        students_by_branch[
                            first_branch
                        ].pop(0)
                    )

                    pair_slot[
                        'available_seats'
                    ].remove(1)

                    assignments.append(
                        {
                            'student': student_1,
                            'room': pair_slot['room'],
                            'row_number': pair_slot[
                                'row_number'
                            ],
                            'table_number': pair_slot[
                                'table_number'
                            ],
                            'seat_number': 1,
                        }
                    )

                    pair_slot[
                        'occupied_branches'
                    ].add(
                        first_branch
                    )

                    # --------------------------------
                    # SECOND BRANCH -> SEAT 2
                    # --------------------------------

                    student_2 = (
                        students_by_branch[
                            second_branch
                        ].pop(0)
                    )

                    pair_slot[
                        'available_seats'
                    ].remove(2)

                    assignments.append(
                        {
                            'student': student_2,
                            'room': pair_slot['room'],
                            'row_number': pair_slot[
                                'row_number'
                            ],
                            'table_number': pair_slot[
                                'table_number'
                            ],
                            'seat_number': 2,
                        }
                    )

                    pair_slot[
                        'occupied_branches'
                    ].add(
                        second_branch
                    )

                    continue

            # ---------------------------------------
            # IF PAIR NOT POSSIBLE
            # FIRST BRANCH ALONE
            # ---------------------------------------

            single_slot = find_single_slot(
                first_branch
            )

            if single_slot:

                student = (
                    students_by_branch[
                        first_branch
                    ].pop(0)
                )

                # Prefer Seat 1
                if 1 in single_slot[
                    'available_seats'
                ]:

                    seat_number = 1

                else:

                    seat_number = (
                        single_slot[
                            'available_seats'
                        ][0]
                    )

                single_slot[
                    'available_seats'
                ].remove(
                    seat_number
                )

                assignments.append(
                    {
                        'student': student,
                        'room': single_slot['room'],
                        'row_number': single_slot[
                            'row_number'
                        ],
                        'table_number': single_slot[
                            'table_number'
                        ],
                        'seat_number': seat_number,
                    }
                )

                single_slot[
                    'occupied_branches'
                ].add(
                    first_branch
                )

                continue

            # ---------------------------------------
            # TRY ANOTHER BRANCH
            # ---------------------------------------

            placed = False

            for branch in branch_names[1:]:

                if not students_by_branch[
                    branch
                ]:

                    continue

                slot = find_single_slot(
                    branch
                )

                if slot:

                    student = (
                        students_by_branch[
                            branch
                        ].pop(0)
                    )

                    # Prefer Seat 1
                    if 1 in slot[
                        'available_seats'
                    ]:

                        seat_number = 1

                    else:

                        seat_number = (
                            slot[
                                'available_seats'
                            ][0]
                        )

                    slot[
                        'available_seats'
                    ].remove(
                        seat_number
                    )

                    assignments.append(
                        {
                            'student': student,
                            'room': slot['room'],
                            'row_number': slot[
                                'row_number'
                            ],
                            'table_number': slot[
                                'table_number'
                            ],
                            'seat_number': seat_number,
                        }
                    )

                    slot[
                        'occupied_branches'
                    ].add(
                        branch
                    )

                    placed = True

                    break

            if placed:

                continue

            # ---------------------------------------
            # NO COMPATIBLE SEAT
            # ---------------------------------------

            break

        # ---------------------------------------
        # CHECK REMAINING STUDENTS
        # ---------------------------------------

        remaining_count = sum(
            len(
                students_by_branch[branch]
            )
            for branch in students_by_branch
        )

        if remaining_count > 0:

            return render(
                request,
                'seating/generate_seating.html',
                {
                    'error': (
                        f'Selected rooms do not have enough '
                        f'compatible empty seats. '
                        f'{remaining_count} student(s) could '
                        f'not be assigned without placing '
                        f'same-branch students at the same table.'
                    ),
                    'exams': exams,
                    'rooms': rooms,
                    'branches': available_branches,
                }
            )

        # ---------------------------------------
        # SAVE SEATING
        #
        # IMPORTANT:
        # Existing exam seating is NOT deleted.
        # ---------------------------------------

        with transaction.atomic():

            for assignment in assignments:

                Seating.objects.create(
                    exam=exam,
                    student=assignment[
                        'student'
                    ],
                    room=assignment[
                        'room'
                    ],
                    row_number=assignment[
                        'row_number'
                    ],
                    table_number=assignment[
                        'table_number'
                    ],
                    seat_number=assignment[
                        'seat_number'
                    ]
                )

        # ---------------------------------------
        # GET GENERATED SEATING
        # ---------------------------------------

        seatings = (
            Seating.objects
            .filter(
                exam=exam
            )
            .select_related(
                'student',
                'room',
                'exam'
            )
            .order_by(
                'room__room_number',
                'row_number',
                'table_number',
                'seat_number'
            )
        )

        # ---------------------------------------
        # REFRESH EXAM LIST
        # ---------------------------------------

        exams = get_available_exams()

        # ---------------------------------------
        # SUCCESS RESPONSE
        # ---------------------------------------

        return render(
            request,
            'seating/generate_seating.html',
            {
                'seatings': seatings,
                'exams': exams,
                'rooms': rooms,
                'branches': available_branches,
                'success': (
                    'Seating arrangement generated successfully.'
                ),
            }
        )

    # ---------------------------------------
    # GET REQUEST
    # ---------------------------------------

    return render(
        request,
        'seating/generate_seating.html',
        {
            'seatings': Seating.objects.none(),
            'exams': exams,
            'rooms': rooms,
            'branches': available_branches,
        }
    )



@login_required
def export_seating_excel(request):

    exam_id = request.GET.get(
        'exam_id'
    )

    if not exam_id:
        return redirect('seat_map')

    try:

        exam = Exam.objects.get(
            id=exam_id
        )

    except Exam.DoesNotExist:

        return HttpResponse(
            "Exam not found.",
            status=404
        )

    seatings = Seating.objects.filter(
        exam=exam
    ).select_related(
        'student',
        'room'
    ).order_by(
        'room__room_number',
        'row_number',
        'table_number',
        'seat_number'
    )

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = (
        "Seating Arrangement"
    )

    headers = [
        "Roll Number",
        "Student Name",
        "Branch",
        "Semester",
        "Room",
        "Row",
        "Table",
        "Seat"
    ]

    worksheet.append(
        headers
    )

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    for seating in seatings:

        worksheet.append([
            seating.student.roll_number,
            seating.student.name,
            seating.student.branch,
            seating.student.semester,
            seating.room.room_number,
            seating.row_number,
            seating.table_number,
            seating.seat_number
        ])

    # ---------------------------------------
    # COLUMN WIDTHS
    # ---------------------------------------

    column_widths = {
        "A": 18,
        "B": 25,
        "C": 20,
        "D": 12,
        "E": 12,
        "F": 10,
        "G": 10,
        "H": 10,
    }

    for column, width in column_widths.items():

        worksheet.column_dimensions[
            column
        ].width = width

    # ---------------------------------------
    # CENTER ALIGNMENT
    # ---------------------------------------

    for row in worksheet.iter_rows():

        for cell in row:

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

    # ---------------------------------------
    # RESPONSE
    # ---------------------------------------

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        f'attachment; filename='
        f'"SEATIFY_{exam.subject}_Seating.xlsx"'
    )

    workbook.save(
        response
    )

    return response