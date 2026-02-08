from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Resume

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm password'}),
        }

ALLOWED_RESUME_EXTENSIONS = ('.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.webp')

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.txt,.doc,.docx,image/jpeg,image/png,image/gif,image/webp',
            }),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        name = getattr(f, 'name', '').lower()
        if not any(name.endswith(ext) for ext in ALLOWED_RESUME_EXTENSIONS):
            raise forms.ValidationError(
                'Allowed formats: PDF, TXT, DOC, DOCX, JPG, PNG, GIF, WEBP.'
            )
        return f

class CareerGuidanceForm(forms.Form):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'e.g. Python, marketing, leadership, data analysis...'}),
        label='Skills & interests',
        required=True
    )