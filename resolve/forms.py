from django import forms
from .models import Issue, Leader


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
            'image': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
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
