from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_home, name='portfolio_home'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photo/<int:photo_id>/delete/', views.delete_photo,
         name='delete_photo'),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
    path('profile/<str:username>/edit/', views.edit_profile_user,
         name='profile_edit_user'),
    path('profile/<str:username>/', views.profile, name='profile_view'),

    path('comment/<int:comment_id>/edit/', views.edit_comment,
         name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment,
         name='delete_comment'),
    path('photo/<int:photo_id>/like/', views.toggle_like,
         name='toggle_like'),

    # Follow URLs
    path('user/<str:username>/follow/', views.follow_user,
         name='follow_user'),
    path('user/<str:username>/unfollow/', views.unfollow_user,
         name='unfollow_user'),
    path('user/<str:username>/followers/', views.followers_list,
         name='followers_list'),
    path('user/<str:username>/following/', views.following_list,
         name='following_list'),

    # Notification URLs
    path('notifications/', views.notifications_list,
         name='notifications_list'),
    path('notifications/count/', views.notifications_unread_count,
         name='notifications_count'),
    path('notifications/dropdown/', views.notifications_dropdown,
         name='notifications_dropdown'),
    path('notifications/<int:notification_id>/read/',
         views.notifications_mark_read, name='notifications_mark_read'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read,
         name='notifications_mark_all_read'),
]
