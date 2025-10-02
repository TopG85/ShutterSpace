from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Profile, Photo, Comment
from .forms import ProfileForm, PhotoForm, CommentForm

# Create your views here.
def portfolio_home(request):
    photos = Photo.objects.filter(is_public=True).order_by('-created_at')[:6]  # Show latest 6 public photos
    # annotate liked state for current user (avoid calling .exists() in templates)
    if request.user.is_authenticated:
        for p in photos:
            p.liked = p.likes.filter(user=request.user).exists()
    else:
        for p in photos:
            p.liked = False
    return render(request, 'portfolio/home.html')

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
    return render(request, 'edit_profile.html', {'form': form, 'profile_owner': request.user})

@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.owner = request.user
            photo.save()
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
    initials = (profile.display_name or user.username).strip()[:2].upper() if profile else user.username[:2].upper()

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
    return render(request, 'photo_detail.html', {'photo': photo, 'comments': comments, 'form': form, 'liked': liked})


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
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})


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
            # photo.image.delete() will remove the file from the configured storage
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
    return JsonResponse({'liked': liked, 'likes_count': photo.likes.count()})


@login_required
def accounts_profile_redirect(request):
    """Redirect /accounts/profile/ to the logged-in user's profile page."""
    username = request.user.username
    return redirect('profile_view', username=username)
