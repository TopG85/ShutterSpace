from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_home, name='portfolio_home'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('photo/<int:photo_id>/comment/', views.add_comment, name='add_comment'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
    path('profile/<str:username>/edit/', views.edit_profile_user, name='profile_edit_user'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('photo/<int:photo_id>/like/', views.toggle_like, name='toggle_like'),
]
