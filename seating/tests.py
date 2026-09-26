from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from exams.models import Exam
from rooms.models import Room
from students.models import Student
from .models import Seating


class SeatingExportTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username='seating-export-admin',
			password='test-password'
		)
		self.client.force_login(user)
		self.student = Student.objects.create(
			name='Export Student',
			roll_number='EXPORT-1',
			enrollment_number='EXPORT-EN-1',
			branch='Science',
			semester=1,
			email='export@example.com'
		)
		self.room = Room.objects.create(
			room_number='EXPORT-ROOM',
			rows=1,
			tables_per_row=1,
			seats_per_table=1
		)
		self.exam = Exam.objects.create(
			exam_name='Export exam',
			subject='Science',
			semester=1,
			exam_date=timezone.localdate(),
			start_time=time(9),
			end_time=time(10)
		)
		Seating.objects.create(
			student=self.student,
			room=self.room,
			exam=self.exam,
			row_number=1,
			table_number=1,
			seat_number=1
		)

	def test_seat_map_supplies_exam_id_for_excel_download(self):
		response = self.client.get(
			reverse('seat_map'),
			{'exam_id': self.exam.id}
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(
			response,
			f"{reverse('export_seating_excel')}?exam_id={self.exam.id}"
		)

		response = self.client.get(
			reverse('export_seating_excel'),
			{'exam_id': self.exam.id}
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response['Content-Type'],
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
		)

	def test_export_without_exam_id_returns_validation_error(self):
		response = self.client.get(reverse('export_seating_excel'))

		self.assertRedirects(response, reverse('seat_map'))
