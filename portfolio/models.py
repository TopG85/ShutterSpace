from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = CloudinaryField('avatar', blank=True)
    hero_image = CloudinaryField(
        'hero_image',
        blank=True,
        help_text="Hero image for your profile page"
    )
    # Additional user-facing profile fields
    display_name = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    show_email = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile({self.user.username})"


class Photo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = CloudinaryField('image')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"Photo({self.title} by {self.owner.username})"


class Comment(models.Model):
    photo = models.ForeignKey(
        Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment({self.author.username} on {self.photo.id})"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(
        Photo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'photo')

    def __str__(self):
        return f"Like({self.user.username} -> {self.photo.id})"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('photo_upload', 'Photo Upload'),
        ('mention', 'Mention'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Notification({self.recipient.username}: {self.title})"

    def get_url(self):
        """Get the URL that this notification should link to"""
        try:
            if self.photo:
                return reverse('photo_detail',
                               kwargs={'photo_id': self.photo.id})
            elif self.sender:
                return reverse('profile_view',
                               kwargs={'username': self.sender.username})
            return reverse('home')
        except Exception:
            # Fallback in case of any URL resolution issues
            return "/"

    def mark_as_read(self):
        """Mark this notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


# auto-create Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
