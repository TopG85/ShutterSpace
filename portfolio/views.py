
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Profile, Photo, Comment, Notification, Follow
from .forms import ProfileForm, PhotoForm, CommentForm


@login_required
def edit_profile(request):
    """Allow the logged-in user to edit their own profile at /profile/edit/."""
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(
        request,
        'edit_profile.html',
        {'form': form, 'profile_owner': request.user}
    )
  

# Create your views here.
@login_required
def portfolio_home(request):
    # Handle search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Search for photos by title or description
        photos = Photo.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query),
            is_public=True
        ).order_by('-created_at')
        # Also search for users
        users = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).distinct()
        # If only one photo matches, redirect to it
        if photos.count() == 1 and users.count() == 0:
            return redirect('photo_detail', pk=photos.first().id)

        # If only one user matches, redirect to their profile
        if users.count() == 1 and photos.count() == 0:
            return redirect('profile_view', username=users.first().username)
    else:
        # Default: show latest photos
        photos = Photo.objects.filter(is_public=True).order_by(
            '-created_at')[:6]
        users = User.objects.none()  # Empty queryset
    # Add liked status for authenticated users
    if request.user.is_authenticated:
        for p in photos:
            p.liked = p.likes.filter(user=request.user).exists()
    else:
        for p in photos:
            p.liked = False
    context = {
        'photos': photos,
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'home.html', context)


def register(request):
    # Redirect logged-in users to home
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Profile is automatically created by the post_save signal
            # After login, user will be redirected to their profile page
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile_user(request, username):
    if request.user.username != username:
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
        {
            'form': form,
            'profile_owner': request.user,
            'profile': profile  # ✅ This makes sidebar access work
        }
    )


@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                photo = form.save(commit=False)
                photo.owner = request.user
                photo.save()

                # Optional: Create notification for followers
                # (if follow system exists)
                # For now, this is a placeholder for future enhancement
                # create_notification_for_followers(request.user, photo)

                return redirect('home')
            except Exception as e:
                # Handle upload errors gracefully
                error_msg = (
                    f"Upload failed: {str(e)}. Please try again with "
                    "a smaller file or different format."
                )
                form.add_error(None, error_msg)
        # If form is not valid, it will be re-rendered with errors
    else:
        form = PhotoForm()

    return render(request, 'upload_photo.html', {'form': form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
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
    followers_count = (
        user.followers.count() if hasattr(user, 'followers') else 0
    )
    following_count = (
        user.following.count() if hasattr(user, 'following') else 0
    )
    joined = user.date_joined
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = user.followers.filter(follower=request.user).exists()
    initials = user.username[:2].upper()

    # Debug: print website value to server log
    if profile:
        print(
            f"[DEBUG] Profile website for {user.username}: '"
            f"{profile.website}'"
        )
    else:
        print(f"[DEBUG] No profile found for {user.username}")
    return render(request, 'profile.html', {
        'user': request.user,
        'owner': user,
        'profile': profile,
        'photos': photos,
        'photos_count': photos_count,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'followers_count': followers_count,
        'following_count': following_count,
        'joined': joined,
        'is_following': is_following,
        'initials': initials,
    })


@login_required
def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    comments = photo.comments.order_by('created_at')
    liked = False
    if request.user.is_authenticated:
        liked = photo.likes.filter(user=request.user).exists()
    if request.method == 'POST' and request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.photo = photo
                comment.author = request.user
                comment.save()
                # Create notification for photo owner
                if photo.owner != request.user:
                    comment_preview = (
                        comment.text[:50] + "..." if len(comment.text) > 50
                        else comment.text
                    )
                    message_text = (
                        f'{request.user.username} commented: '
                        f'"{comment_preview}"'
                    )
                    # PEP8: break long line
                    message_text = (
                        f'{request.user.username} commented: '  # noqa: E501
                        f'"{comment_preview}"'
                    )
                    # PEP8: break long line
                    message_text = (
                        f'{request.user.username} commented: '  # noqa: E501
                        f'"{comment_preview}"'
                    )
                    # PEP8: break long line
                    message_text = (
                        f'{request.user.username} commented: '
                        f'"{comment_preview}"'
                    )
                    # PEP8: break long line
                    message_text = (
                        f'{request.user.username} commented: '
                        f'"{comment_preview}"'
                    )
                    # PEP8: break long line
                    message_text = (
                        f'{request.user.username} commented: '
                        f'"{comment_preview}"'
                    )
                    create_notification(
                        recipient=photo.owner,
                        sender=request.user,
                        notification_type='comment',
                        title='New comment on your photo',
                        message=message_text,
                        photo=photo,
                        comment=comment
                    )
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'author': request.user.username,
                        'created_at': comment.created_at.strftime(
                            '%b %d, %Y %H:%M'),
                        'text': comment.text
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid comment.'
                })
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.photo = photo
                comment.author = request.user
                comment.save()
                if photo.owner != request.user:
                    comment_preview = (
                        comment.text[:50] + "..." if len(comment.text) > 50
                        else comment.text
                    )
                    message_text = (
                        f'{request.user.username} commented: '
                        f'"{comment_preview}"'
                    )
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
    # Ensure all code paths return a response
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
    # Only comment authors can edit their own comments
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('photo_detail', photo_id=comment.photo.id)
    else:
        form = CommentForm(instance=comment)
    # No longer render a separate edit_comment.html; redirect to photo_detail
    return redirect('photo_detail', photo_id=comment.photo.id)


@login_required
def delete_comment(request, comment_id):
    """Allow comment authors and photo owners to delete comments.
    GET: Show confirmation page
    POST: Actually delete the comment
    """
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if user is either the comment author or the photo owner
    if comment.author != request.user and comment.photo.owner != request.user:
        # User is neither the comment author nor the photo owner
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden(
            "You don't have permission to delete this comment."
        )

    if request.method == 'POST':
        # Delete the comment and redirect
        photo_id = comment.photo.id
        comment.delete()
        return redirect('photo_detail', photo_id=photo_id)
    # If GET, show confirmation template
    return render(request, 'confirm_delete_comment.html', {
        'comment': comment,
        'photo': comment.photo
    })


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
    # Filter: show only unread by default, or all if requested
    show = request.GET.get('show', 'unread')
    if show == 'all':
        notifications = request.user.notifications.all()[:20]
    else:
        notifications = request.user.notifications.filter(is_read=False)[:20]
    unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'show': show
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
    # Show up to 5 unread notifications only
    notifications = list(
        request.user.notifications.filter(is_read=False)
        .order_by('-created_at')[:5]
    )
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'url': notification.get_url(),
            'sender_username': (
                notification.sender.username if notification.sender else None
            ),
            'type': notification.notification_type
        })
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })


@login_required
def follow_user(request, username):
    """Follow a user"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)
        # Can't follow yourself
        if user_to_follow == request.user:
            return JsonResponse({
                'success': False,
                'error': 'Cannot follow yourself'
            })
        # Create or get the follow relationship
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        if created:
            # Create notification for the followed user
            create_notification(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow',
                title='New Follower',
                message=f'{request.user.username} started following you!'
            )
            return JsonResponse({
                'success': True,
                'action': 'followed',
                'followers_count': user_to_follow.followers.count()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Already following this user'
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def unfollow_user(request, username):
    """Unfollow a user"""
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(User, username=username)
        # Try to find and delete the follow relationship
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            return JsonResponse({
                'success': True,
                'action': 'unfollowed',
                'followers_count': user_to_unfollow.followers.count()
            })
        except Follow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Not following this user'
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def followers_list(request, username):
    """Display a user's followers"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.select_related('follower__profile').all()
    return render(request, 'followers_list.html', {
        'user': user,
        'followers': followers,
        'title': f"{user.username}'s Followers"
    })


@login_required
def following_list(request, username):
    """Display users that this user is following"""
    user = get_object_or_404(User, username=username)
    following = user.following.select_related('following__profile').all()
    return render(request, 'following_list.html', {
        'user': user,
        'following': following,
        'title': f"Users {user.username} is Following"
    })
