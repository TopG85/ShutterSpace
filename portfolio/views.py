from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import Profile, Photo, Comment, Notification
from .forms import ProfileForm, PhotoForm, CommentForm


# Create your views here.


def portfolio_home(request):
    photos = Photo.objects.filter(is_public=True).order_by('-created_at')[:6]
    if request.user.is_authenticated:
        for p in photos:
            p.liked = p.likes.filter(user=request.user).exists()
    else:
        for p in photos:
            p.liked = False
    return render(request, 'home.html', {'photos': photos})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # auto-create profile
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def edit_profile_user(request, username):
    """Allow the owner to edit their profile at /profile/<username>/edit/.
    Redirects non-owners to the public profile view.
    """
    if request.user.username != username:
        # optionally allow staff to edit others; currently redirect
        return redirect('profile_view', username=username)

    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=username)
    else:
        form = ProfileForm(instance=profile)
    return render(
        request,
        'edit_profile.html',
        {'form': form, 'profile_owner': request.user}
    )


@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.owner = request.user
            photo.save()
            
            # Optional: Create notification for followers
            # (if follow system exists)
            # For now, this is a placeholder for future enhancement
            # create_notification_for_followers(request.user, photo)
            
            return redirect('home')
    else:
        form = PhotoForm()
    return render(request, 'upload_photo.html', {'form': form})


@login_required
def add_comment(request, photo_id):
    photo = Photo.objects.get(id=photo_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.photo = photo
            comment.author = request.user
            comment.save()
            
            # Create notification for photo owner
            comment_preview = (comment.text[:50] + "..."
                               if len(comment.text) > 50 else comment.text)
            message_text = (f'{request.user.username} commented: '
                            f'"{comment_preview}"')
            create_notification(
                recipient=photo.owner,
                sender=request.user,
                notification_type='comment',
                title='New comment on your photo',
                message=message_text,
                photo=photo,
                comment=comment
            )
            
            return redirect('photo_detail', photo_id=photo.id)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'photo': photo})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.filter(user=user).first()
    photos = Photo.objects.filter(owner=user).order_by('-created_at')
    if request.user.is_authenticated:
        for p in photos:
            p.liked = p.likes.filter(user=request.user).exists()
    else:
        for p in photos:
            p.liked = False
    # compute simple stats
    photos_count = photos.count()
    total_likes = sum(p.likes.count() for p in photos)
    total_comments = sum(p.comments.count() for p in photos)
    joined = user.date_joined
    # initials fallback for avatar
    if profile:
        display_name = profile.display_name or user.username
        initials = display_name.strip()[:2].upper()
    else:
        initials = user.username[:2].upper()

    context = {
        'profile': profile,
        'photos': photos,
        'owner': user,
        'photos_count': photos_count,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'joined': joined,
        'initials': initials,
    }
    return render(request, 'profile.html', context)


def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    comments = photo.comments.order_by('created_at')
    liked = False
    if request.user.is_authenticated:
        liked = photo.likes.filter(user=request.user).exists()
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.photo = photo
            comment.author = request.user
            comment.save()
            return redirect('photo_detail', photo_id=photo.id)
    else:
        form = CommentForm()
    return render(
        request,
        'photo_detail.html',
        {
            'photo': photo,
            'comments': comments,
            'form': form,
            'liked': liked
        }
    )


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('photo_detail', photo_id=comment.photo.id)
    else:
        form = CommentForm(instance=comment)
    return render(
        request,
        'edit_comment.html',
        {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()
    return redirect('photo_detail', photo_id=comment.photo.id)


@login_required
def delete_photo(request, photo_id):
    """Allow the owner to delete a photo and its stored file.

    Uses POST to perform deletion (CSRF protected). After deletion redirect
    to the owner's profile page.
    """
    photo = get_object_or_404(Photo, id=photo_id, owner=request.user)
    if request.method == 'POST':
        # Attempt to delete the underlying file from storage, then the model
        try:
            # photo.image.delete() will remove the file from the
            # configured storage
            photo.image.delete(save=False)
        except Exception:
            # ignore storage deletion errors; proceed to delete DB record
            pass
        photo.delete()
        return redirect('profile_view', username=request.user.username)
    # If GET, show a simple confirmation template
    return render(request, 'confirm_delete_photo.html', {'photo': photo})


@login_required
def toggle_like(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    like = photo.likes.filter(user=request.user).first()
    if like:
        like.delete()
        liked = False
    else:
        photo.likes.create(user=request.user)
        liked = True
        
        # Create notification for photo owner when liked (not unliked)
        like_message = (f'{request.user.username} liked your photo '
                        f'"{photo.title}"')
        create_notification(
            recipient=photo.owner,
            sender=request.user,
            notification_type='like',
            title='Someone liked your photo',
            message=like_message,
            photo=photo
        )
        
    return JsonResponse({'liked': liked, 'likes_count': photo.likes.count()})


@login_required
def accounts_profile_redirect(request):
    """Redirect /accounts/profile/ to the logged-in user's profile page."""
    username = request.user.username
    return redirect('profile_view', username=username)


# ===== NOTIFICATION SYSTEM =====

def create_notification(recipient, sender, notification_type, title, message,
                        photo=None, comment=None):
    """
    Utility function to create notifications
    """
    # Don't create notification if sender is same as recipient
    if sender == recipient:
        return None
    
    # Create the notification
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        photo=photo,
        comment=comment
    )
    return notification


@login_required
def notifications_list(request):
    """Display all notifications for the current user"""
    # Latest 20 notifications
    notifications = request.user.notifications.all()[:20]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notifications_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
def notifications_mark_read(request, notification_id):
    """AJAX endpoint to mark a specific notification as read"""
    try:
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notifications_mark_all_read(request):
    """AJAX endpoint to mark all notifications as read"""
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def notifications_dropdown(request):
    """AJAX endpoint to get recent notifications for dropdown"""
    # Latest 5 for dropdown
    recent_notifications = request.user.notifications.all()[:5]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    notifications_data = []
    for notification in recent_notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'url': notification.get_url(),
            'sender_username': (notification.sender.username
                                if notification.sender else None),
            'type': notification.notification_type
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })
