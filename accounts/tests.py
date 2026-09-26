from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminPanelTests(TestCase):
	def test_panel_requires_login_and_renders_workflows(self):
		response = self.client.get(reverse('admin_panel'))
		self.assertRedirects(
			response,
			f"{reverse('faculty_login')}?next={reverse('admin_panel')}"
		)
		protected_pages = (
			'student_list',
			'add_student',
			'upload_students',
			'room_list',
			'add_room',
			'exam_list',
			'add_exam',
			'upload_timetable',
			'seat_map',
			'generate_seating',
			'export_seating_excel',
		)
		for page_name in protected_pages:
			with self.subTest(page=page_name):
				response = self.client.get(reverse(page_name))
				self.assertEqual(response.status_code, 302)
		self.assertEqual(
			self.client.get(reverse('student_seat')).status_code,
			200
		)

		user_model = get_user_model()
		user = user_model.objects.create_user(
			username='panel-user',
			password='test-password'
		)
		self.client.force_login(user)

		response = self.client.get(reverse('admin_panel'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Admin panel')
		self.assertContains(response, reverse('student_list'))
		self.assertContains(response, reverse('upload_timetable'))
		self.assertContains(response, reverse('generate_seating'))
		self.assertContains(response, reverse('seat_map'))
		self.assertNotContains(response, reverse('export_seating_excel'))
		self.assertContains(response, '0 exams need a seating plan')
