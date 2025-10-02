from django import forms
from .models import Photo, Comment, Profile
from cloudinary.forms import CloudinaryFileField


class PhotoForm(forms.ModelForm):
    image = CloudinaryFileField(
        options={
            'crop': 'limit',
            'width': 2000,
            'height': 2000,
            'quality': 'auto:eco',  # More aggressive compression
            'format': 'auto',  # Auto-select best format (WebP when supported)
            'fetch_format': 'auto',  # Enable automatic format delivery
            'progressive': True,  # Progressive JPEG loading
            'secure': True  # Use HTTPS URLs
        }
    )
    
    class Meta:
        model = Photo
        fields = ['image', 'title', 'description', 'is_public']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class ProfileForm(forms.ModelForm):
    avatar = CloudinaryFileField(
        required=False,
        options={
            'crop': 'thumb',
            'width': 300,
            'height': 300,
            'gravity': 'face',
            'quality': 'auto:eco',  # Better compression for avatars
            'format': 'auto',  # Auto WebP format
            'progressive': True,
            'secure': True
        }
    )
    hero_image = CloudinaryFileField(
        required=False,
        options={
            'crop': 'fill',
            'width': 1200,
            'height': 400,
            'gravity': 'auto',
            'quality': 'auto:eco',  # Better compression for hero images
            'format': 'auto',  # Auto WebP format
            'progressive': True,
            'secure': True
        }
    )
    
    class Meta:
        model = Profile
        fields = [
            'display_name', 'bio', 'avatar', 'hero_image',
            'website', 'location', 'instagram', 'show_email'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
            'show_email': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
