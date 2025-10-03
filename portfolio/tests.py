from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Photo, Comment, Profile, Like, Notification
from .forms import CommentForm, ProfileForm


class CommentWorkflowTests(TestCase):
    """Test commenting functionality on photos"""

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='photographer1',
            email='photo1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='photographer2',
            email='photo2@test.com',
            password='testpass123'
        )

        # Create test image
        gif_data = b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x0C\x0A\x00\x3B'
        test_image = SimpleUploadedFile(
            name='test_image.gif',
            content=gif_data,
            content_type='image/gif'
        )

        # Create test photo
        self.photo = Photo.objects.create(
            title='Test Photo',
            description='Test description',
            photographer=self.user1,
            image=test_image
        )

    def test_post_comment_and_display(self):
        """Test that comments can be posted and displayed"""
        self.client.login(username='photographer2', password='testpass123')

        # Post a comment
        response = self.client.post(
            reverse('add_comment', kwargs={'photo_id': self.photo.id}),
            {'content': 'Great photo!'}
        )

        # Should redirect back to photo detail
        self.assertRedirects(
            response,
            reverse('photo_detail', kwargs={'photo_id': self.photo.id})
        )

        # Check comment appears on photo detail page
        response = self.client.get(
            reverse('photo_detail', kwargs={'photo_id': self.photo.id})
        )
        self.assertContains(response, 'Great photo!')

    def test_owner_can_delete_photo(self):
        """Test that photo owners can delete their own photos"""
        self.client.login(username='photographer1', password='testpass123')

        # Delete the photo
        response = self.client.post(
            reverse('delete_photo', kwargs={'photo_id': self.photo.id})
        )

        # Should redirect to home
        self.assertRedirects(response, reverse('home'))

        # Photo should be deleted
        self.assertFalse(
            Photo.objects.filter(id=self.photo.id).exists()
        )

    def test_non_owner_cannot_delete_photo(self):
        """Test that non-owners cannot delete photos"""
        self.client.login(username='photographer2', password='testpass123')

        # Try to delete the photo
        response = self.client.post(
            reverse('delete_photo', kwargs={'photo_id': self.photo.id})
        )

        # Should get forbidden
        self.assertEqual(response.status_code, 403)

        # Photo should still exist
        self.assertTrue(
            Photo.objects.filter(id=self.photo.id).exists()
        )


class NotificationTests(TestCase):
    """Test notification system functionality"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        gif_data = b'\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02\x0C\x0A\x00\x3B'
        test_image = SimpleUploadedFile(
            name='test_image.gif',
            content=gif_data,
            content_type='image/gif'
        )

        self.photo = Photo.objects.create(
            title='Test Photo',
            photographer=self.user1,
            image=test_image
        )

    def test_like_notification_creation(self):
        """Test notification is created when photo is liked"""
        self.client.login(username='user2', password='testpass123')
        self.client.post(
            reverse('like_photo', kwargs={'photo_id': self.photo.id})
        )

        # Check notification was created
        notification = Notification.objects.filter(
            user=self.user1,
            notification_type='like'
        ).first()
        self.assertIsNotNone(notification)

    def test_comment_notification_creation(self):
        """Test notification is created when commented on"""
        self.client.login(username='user2', password='testpass123')
        self.client.post(
            reverse('add_comment', kwargs={'photo_id': self.photo.id}),
            {'content': 'Great photo!'}
        )

        # Check notification was created
        notification = Notification.objects.filter(
            user=self.user1,
            notification_type='comment'
        ).first()
        self.assertIsNotNone(notification)

    def test_notification_url_generation(self):
        """Test notification URL generation works correctly"""
        notification = Notification.objects.create(
            user=self.user1,
            notification_type='like',
            message='Test notification',
            photo=self.photo
        )
        expected_url = f'/portfolio/photo/{self.photo.id}/'
        self.assertEqual(notification.get_url(), expected_url)


class SecurityTests(TestCase):
    """Test security and authentication requirements"""

    def test_login_required_for_upload(self):
        """Test that photo upload requires authentication"""
        response = self.client.get(reverse('upload_photo'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=/portfolio/upload/'
        )

    def test_notifications_require_login(self):
        """Test that notifications API requires authentication"""
        response = self.client.get(reverse('notifications_api'))
        expected = '/accounts/login/?next=/portfolio/notifications/api/'
        self.assertRedirects(response, expected)
