from django.contrib import admin
from .models import Profile, Photo, Comment, Like


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'user__email']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['photo', 'author', 'created_at', 'text']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username', 'photo__title']
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo', 'created_at']
    search_fields = ['user__username', 'photo__title']
