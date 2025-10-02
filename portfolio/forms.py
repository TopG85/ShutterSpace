from django import forms
from .models import Photo, Comment, Profile
from django.contrib.auth.models import User

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'title', 'description', 'is_public']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ProfileForm(forms.ModelForm):
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
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
