from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rooms.models import Room
from seating.models import Seating
from students.models import Student
from .models import Exam


class ExamCrudTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username='exam-admin',
			password='test-password'
		)
		self.client.force_login(user)

	def test_create_edit_and_confirm_exam_delete(self):
		exam_data = {
			'exam_name': 'Midterm',
			'subject': 'Biology',
			'semester': 2,
			'exam_date': date.today().isoformat(),
			'start_time': '09:00',
			'end_time': '10:00',
			'status': 'Upcoming',
		}
		response = self.client.post(reverse('add_exam'), exam_data)
		self.assertRedirects(response, reverse('exam_list'))
		exam = Exam.objects.get(exam_name='Midterm')

		exam_data['subject'] = 'Chemistry'
		response = self.client.post(
			reverse('edit_exam', args=[exam.id]),
			exam_data
		)
		self.assertRedirects(response, reverse('exam_list'))
		exam.refresh_from_db()
		self.assertEqual(exam.subject, 'Chemistry')

		student = Student.objects.create(
			name='Exam Student', roll_number='EX-100',
			enrollment_number='EX-EN-100', branch='Science', semester=2,
			email='exam@example.com'
		)
		room = Room.objects.create(
			room_number='EX-ROOM', rows=1, tables_per_row=1, seats_per_table=1
		)
		Seating.objects.create(
			student=student, room=room, exam=exam,
			row_number=1, table_number=1, seat_number=1
		)

		delete_url = reverse('delete_exam', args=[exam.id])
		self.assertContains(self.client.get(delete_url), '1 seating assignment')
		response = self.client.post(delete_url)

		self.assertRedirects(response, reverse('exam_list'))
		self.assertFalse(Exam.objects.filter(pk=exam.pk).exists())
		self.assertFalse(Seating.objects.filter(exam=exam).exists())
