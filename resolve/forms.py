from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Issue, Leader, CitizenProfile, Comment, Hashtag


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'image', 'leader_tagged']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the problem'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'leader_tagged': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        # Exclude latitude and longitude as they will be populated by JavaScript
        exclude = ['latitude', 'longitude', 'user', 'status', 'is_leader_resolved', 
                  'is_user_confirmed', 'flag_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate leader choices
        self.fields['leader_tagged'].queryset = Leader.objects.all()
        self.fields['leader_tagged'].empty_label = "Select a leader to tag"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write a comment...'
            })
        }


class IssueShareForm(forms.Form):
    caption = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 2,
        'placeholder': 'Add a caption to your share...'
    }))
    share_to_profile = forms.BooleanField(required=False, initial=True)


class HashtagForm(forms.ModelForm):
    class Meta:
        model = Hashtag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add hashtags (e.g., cleancity, roadrepair)'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Remove # if user added it
        return name.lstrip('#').lower()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CitizenProfile
        fields = ['real_name', 'contact_email', 'profile_picture', 'bio', 'website',
                 'hometown_name', 'hometown_latitude', 'hometown_longitude']
        widgets = {
            'real_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'hometown_name': forms.HiddenInput(),
            'hometown_latitude': forms.HiddenInput(),
            'hometown_longitude': forms.HiddenInput(),
        }

class SignupForm(UserCreationForm):
    real_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your full name'
    }))
    contact_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your email address'
    }))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Tell us about yourself...',
        'rows': 3
    }))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your website (optional)'
    }))
    hometown_name = forms.CharField(widget=forms.HiddenInput())
    hometown_latitude = forms.DecimalField(max_digits=22, decimal_places=16, widget=forms.HiddenInput())
    hometown_longitude = forms.DecimalField(max_digits=22, decimal_places=16, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('username', 'real_name', 'contact_email', 'password1', 'password2',
                 'hometown_name', 'hometown_latitude', 'hometown_longitude')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }

    def save(self, commit=True):
        user = super().save(commit=True)
        
        # Get or create CitizenProfile
        CitizenProfile.objects.update_or_create(
            user=user,
            defaults={
                'real_name': self.cleaned_data['real_name'],
                'contact_email': self.cleaned_data['contact_email'],
                'hometown_name': self.cleaned_data['hometown_name'],
                'hometown_latitude': self.cleaned_data['hometown_latitude'],
                'hometown_longitude': self.cleaned_data['hometown_longitude']
            }
        )
        
        return user
