from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
import re
from .models import Photo, Comment, Profile
from cloudinary.forms import CloudinaryFileField


class PhotoForm(forms.ModelForm):
    image = CloudinaryFileField(
        options={
            'crop': 'limit',
            'width': 2000,
            'height': 2000,
            'quality': 'auto:eco',  # More aggressive compression
            'progressive': True,  # Progressive JPEG loading
            'secure': True  # Use HTTPS URLs
        },
        help_text=("Upload a high-quality image (JPEG, PNG, or WebP). "
                   "Maximum file size: 10MB.")
    )
    
    class Meta:
        model = Photo
        fields = ['image', 'title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a descriptive title for your photo',
                'maxlength': '255'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': ('Describe your photo, camera settings, '
                                'location, or story...'),
                'maxlength': '1000'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Photo Title *',
            'description': 'Description',
            'is_public': 'Make this photo public',
            'image': 'Upload Photo *'
        }
        help_texts = {
            'title': 'Choose a clear, descriptive title (3-255 characters)',
            'description': ('Add details about your photo '
                            '(optional, max 1000 characters)'),
            'is_public': 'Uncheck to keep this photo private'
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Photo title is required.")
        
        title = title.strip()
        if len(title) < 3:
            raise ValidationError("Title must be at least 3 characters long.")
        
        if len(title) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")
        
        # Check for inappropriate content (basic filter)
        inappropriate_words = ['spam', 'test123', 'asdf']
        if any(word in title.lower() for word in inappropriate_words):
            raise ValidationError("Please use a more descriptive title.")
        
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if description:
            description = description.strip()
            if len(description) > 1000:
                raise ValidationError("Description too long (max 1000 chars).")
        return description
    
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        description = cleaned_data.get('description', '')
        
        # Ensure title and description aren't identical
        if (title and description and
                title.strip().lower() == description.strip().lower()):
            raise ValidationError(
                "Title and description should be different.")
        
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts about this photo...',
                'maxlength': '500'
            })
        }
        labels = {
            'text': 'Your Comment *'
        }
        help_texts = {
            'text': 'Be respectful and constructive (max 500 characters)'
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise ValidationError("Comment cannot be empty.")
        
        text = text.strip()
        if len(text) < 2:
            raise ValidationError("Comment too short (min 2 chars).")
        
        if len(text) > 500:
            raise ValidationError("Comment too long (max 500 chars).")
        
        # Basic spam detection
        if text.count('http') > 2:
            raise ValidationError("Too many links not allowed.")
        
        # Check for excessive repetition
        words = text.lower().split()
        if len(words) > 0:
            most_common_word = max(set(words), key=words.count)
            if words.count(most_common_word) > len(words) * 0.5 and len(words) > 4:
                raise ValidationError("Please write a more varied comment.")
        
        return text


class ProfileForm(forms.ModelForm):
    avatar = CloudinaryFileField(
        required=False,
        options={
            'crop': 'thumb',
            'width': 300,
            'height': 300,
            'gravity': 'face',
            'quality': 'auto:eco',  # Better compression for avatars
            'progressive': True,
            'secure': True
        },
        help_text="Upload a profile photo (JPEG, PNG, or WebP). Square images work best."
    )
    hero_image = CloudinaryFileField(
        required=False,
        options={
            'crop': 'fill',
            'width': 1200,
            'height': 400,
            'gravity': 'auto',
            'quality': 'auto:eco',  # Better compression for hero images
            'progressive': True,
            'secure': True
        },
        help_text="Upload a header image for your profile (1200x400px recommended)."
    )
    
    class Meta:
        model = Profile
        fields = [
            'display_name', 'bio', 'avatar', 'hero_image',
            'website', 'location', 'instagram', 'show_email'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your display name',
                'maxlength': '150'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself, your photography style, interests...',
                'maxlength': '500'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-website.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country',
                'maxlength': '150'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'your_instagram_handle',
                'maxlength': '100'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'display_name': 'Display Name',
            'bio': 'Biography',
            'avatar': 'Profile Photo',
            'hero_image': 'Header Image',
            'website': 'Website',
            'location': 'Location',
            'instagram': 'Instagram Handle',
            'show_email': 'Show Email Publicly'
        }
        help_texts = {
            'display_name': 'How you want to be known on ShutterSpace (optional)',
            'bio': 'Share your photography story (max 500 characters)',
            'website': 'Your personal website or portfolio URL',
            'location': 'Where you are based',
            'instagram': 'Your Instagram username (without @)',
            'show_email': 'Allow other users to see your email address'
        }
    
    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name', '')
        if display_name:
            display_name = display_name.strip()
            if len(display_name) < 2:
                raise ValidationError("Display name must be at least 2 characters long.")
            if len(display_name) > 150:
                raise ValidationError("Display name cannot exceed 150 characters.")
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', display_name):
                raise ValidationError("Display name can only contain letters, numbers, spaces, hyphens, underscores, and periods.")
        
        return display_name
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if bio:
            bio = bio.strip()
            if len(bio) > 500:
                raise ValidationError("Biography cannot exceed 500 characters.")
            
            # Check for minimum meaningful length if provided
            if len(bio) < 10:
                raise ValidationError("If you provide a bio, please write at least 10 characters to tell us about yourself.")
        
        return bio
    
    def clean_website(self):
        website = self.cleaned_data.get('website', '')
        if website:
            website = website.strip()
            # Ensure URL has protocol
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            # Validate URL format
            validator = URLValidator()
            try:
                validator(website)
            except ValidationError:
                raise ValidationError("Please enter a valid website URL (e.g., https://example.com)")
        
        return website
    
    def clean_location(self):
        location = self.cleaned_data.get('location', '')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise ValidationError("Location must be at least 2 characters long.")
            if len(location) > 150:
                raise ValidationError("Location cannot exceed 150 characters.")
            
            # Basic format validation
            if not re.match(r'^[a-zA-Z0-9\s\-,\.]+$', location):
                raise ValidationError("Location can only contain letters, numbers, spaces, hyphens, commas, and periods.")
        
        return location
    
    def clean_instagram(self):
        instagram = self.cleaned_data.get('instagram', '')
        if instagram:
            instagram = instagram.strip()
            # Remove @ if user included it
            if instagram.startswith('@'):
                instagram = instagram[1:]
            
            if len(instagram) < 1:
                raise ValidationError("Instagram handle cannot be empty.")
            if len(instagram) > 30:
                raise ValidationError("Instagram handle cannot exceed 30 characters.")
            
            # Validate Instagram handle format
            if not re.match(r'^[a-zA-Z0-9_.]+$', instagram):
                raise ValidationError("Instagram handle can only contain letters, numbers, underscores, and periods.")
            
            if instagram.startswith('.') or instagram.endswith('.'):
                raise ValidationError("Instagram handle cannot start or end with a period.")
            
            if '..' in instagram:
                raise ValidationError("Instagram handle cannot contain consecutive periods.")
        
        return instagram
    
    def clean(self):
        cleaned_data = super().clean()
        display_name = cleaned_data.get('display_name')
        bio = cleaned_data.get('bio')
        
        # If user provides a display name, encourage them to add a bio
        if display_name and not bio:
            self.add_error('bio', "Consider adding a biography to tell others about yourself.")
        
        return cleaned_data
