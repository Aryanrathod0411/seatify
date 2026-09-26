from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from exams.models import Exam
from seating.models import Seating
from students.models import Student
from .models import Room


class RoomCrudTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username='room-admin',
			password='test-password'
		)
		self.client.force_login(user)

	def test_create_edit_and_confirm_room_delete(self):
		room_data = {
			'room_number': 'B-10',
			'rows': 2,
			'tables_per_row': 3,
			'seats_per_table': 2,
		}
		response = self.client.post(reverse('add_room'), room_data)
		self.assertRedirects(response, reverse('room_list'))
		room = Room.objects.get(room_number='B-10')

		room_data['rows'] = 4
		response = self.client.post(
			reverse('edit_room', args=[room.id]),
			room_data
		)
		self.assertRedirects(response, reverse('room_list'))
		room.refresh_from_db()
		self.assertEqual(room.rows, 4)

		student = Student.objects.create(
			name='Room Student', roll_number='RM-100',
			enrollment_number='RM-EN-100', branch='Science', semester=2,
			email='room@example.com'
		)
		exam = Exam.objects.create(
			exam_name='Room test', subject='Science', semester=2,
			exam_date=date.today(), start_time=time(9), end_time=time(10)
		)
		Seating.objects.create(
			student=student, room=room, exam=exam,
			row_number=4, table_number=1, seat_number=1
		)

		reduced_room_data = {**room_data, 'rows': 3}
		response = self.client.post(
			reverse('edit_room', args=[room.id]),
			reduced_room_data
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Room size cannot be smaller')
		room.refresh_from_db()
		self.assertEqual(room.rows, 4)

		delete_url = reverse('delete_room', args=[room.id])
		self.assertContains(self.client.get(delete_url), '1 seating assignment')
		response = self.client.post(delete_url)

		self.assertRedirects(response, reverse('room_list'))
		self.assertFalse(Room.objects.filter(pk=room.pk).exists())
		self.assertFalse(Seating.objects.filter(room=room).exists())
