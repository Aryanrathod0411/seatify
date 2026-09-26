from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from exams.models import Exam
from rooms.models import Room
from seating.models import Seating
from .models import Student


class StudentCrudTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username='student-admin',
			password='test-password'
		)
		self.client.force_login(user)

	def test_create_edit_and_confirm_student_delete(self):
		response = self.client.post(
			reverse('add_student'),
			{
				'name': 'Jamie Student',
				'roll_number': 'ST-100',
				'enrollment_number': 'EN-100',
				'branch': 'Science',
				'semester': 2,
				'email': 'jamie@example.com',
			}
		)
		self.assertRedirects(response, reverse('student_list'))
		student = Student.objects.get(roll_number='ST-100')

		response = self.client.post(
			reverse('edit_student', args=[student.id]),
			{
				'name': 'Jamie Updated',
				'roll_number': 'ST-100',
				'enrollment_number': 'EN-100',
				'branch': 'Science',
				'semester': 3,
				'email': 'jamie@example.com',
			}
		)
		self.assertRedirects(response, reverse('student_list'))
		student.refresh_from_db()
		self.assertEqual(student.name, 'Jamie Updated')
		self.assertEqual(student.semester, 3)

		room = Room.objects.create(
			room_number='ST-ROOM', rows=1, tables_per_row=1, seats_per_table=1
		)
		exam = Exam.objects.create(
			exam_name='Student test', subject='Science', semester=3,
			exam_date=date.today(), start_time=time(9), end_time=time(10)
		)
		Seating.objects.create(
			student=student, room=room, exam=exam,
			row_number=1, table_number=1, seat_number=1
		)

		delete_url = reverse('delete_student', args=[student.id])
		self.assertContains(self.client.get(delete_url), '1 seating assignment')
		response = self.client.post(delete_url)

		self.assertRedirects(response, reverse('student_list'))
		self.assertFalse(Student.objects.filter(pk=student.pk).exists())
		self.assertFalse(Seating.objects.filter(student=student).exists())


class EnrollmentLookupTests(TestCase):
	def test_student_search_uses_enrollment_number(self):
		user = get_user_model().objects.create_user(
			username='enrollment-search-admin',
			password='test-password'
		)
		self.client.force_login(user)
		student = Student.objects.create(
			name='Searchable Student',
			roll_number='ROLL-LOOKUP-1',
			enrollment_number='ENR-2024-LOOKUP-1',
			branch='Science',
			semester=2,
			email='lookup@example.com'
		)

		response = self.client.get(
			reverse('student_list'),
			{'search': 'ENR-2024-LOOKUP-1'}
		)
		self.assertContains(response, 'Searchable Student')

		response = self.client.get(
			reverse('student_list'),
			{'search': 'ROLL-LOOKUP-1'}
		)
		self.assertFalse(
			response.context['students'].filter(pk=student.pk).exists()
		)

	def test_seat_lookup_uses_enrollment_number(self):
		student = Student.objects.create(
			name='Seat Lookup Student',
			roll_number='ROLL-SEAT-1',
			enrollment_number='ENROLL-SEAT-1',
			branch='Science',
			semester=2,
			email='seat-lookup@example.com'
		)
		room = Room.objects.create(
			room_number='LOOKUP-ROOM',
			rows=1,
			tables_per_row=1,
			seats_per_table=1
		)
		exam = Exam.objects.create(
			exam_name='Seat lookup exam',
			subject='Science',
			semester=2,
			exam_date=date.today(),
			start_time=time(9),
			end_time=time(10)
		)
		seating = Seating.objects.create(
			student=student,
			room=room,
			exam=exam,
			row_number=1,
			table_number=1,
			seat_number=1
		)

		response = self.client.post(
			reverse('student_seat'),
			{
				'enrollment_number': 'ENROLL-SEAT-1',
				'exam_id': exam.id,
			}
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['seating'], seating)
		self.assertContains(response, 'ENROLL-SEAT-1')
		self.assertContains(response, 'Seat 1')

		response = self.client.post(
			reverse('student_seat'),
			{
				'enrollment_number': 'ROLL-SEAT-1',
				'exam_id': exam.id,
			}
		)
		self.assertContains(response, 'No seating found for this enrollment number.')
