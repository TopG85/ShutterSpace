from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Photo, Comment
from django.core.files.uploadedfile import SimpleUploadedFile


class CommentWorkflowTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='tester', password='pass')
		# create a small in-memory image file
		img = SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46\x38\x39\x61', content_type='image/gif')
		self.photo = Photo.objects.create(owner=self.user, image=img, title='Test', description='desc')

	def test_post_comment_and_display(self):
		self.client.login(username='tester', password='pass')
		url = f"/portfolio/photo/{self.photo.id}/"
		resp = self.client.post(url, {'text': 'Nice shot!'}, follow=True)
		self.assertEqual(resp.status_code, 200)
		# Check the comment was created
		self.assertTrue(Comment.objects.filter(photo=self.photo, author=self.user, text='Nice shot!').exists())
		# Response should include comment text
		self.assertContains(resp, 'Nice shot!')
