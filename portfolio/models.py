from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment({self.author.username} on {self.photo.id})"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'photo')

    def __str__(self):
        return f"Like({self.user.username} -> {self.photo.id})"


# auto-create Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
