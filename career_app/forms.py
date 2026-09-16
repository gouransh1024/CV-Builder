from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Resume, ResumeDraft


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm password'}),
        }


ALLOWED_RESUME_EXTENSIONS = ('.pdf', '.txt', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.webp')
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

TARGET_ROLE_CHOICES = [
    ('', 'Auto-detect / General'),
    ('software_developer', 'Software Developer'),
    ('frontend_developer', 'Frontend Developer'),
    ('backend_developer', 'Backend Developer'),
    ('data_analyst', 'Data Analyst'),
    ('devops_engineer', 'DevOps Engineer'),
    ('product_manager', 'Product Manager'),
]


class ResumeUploadForm(forms.ModelForm):
    target_role = forms.ChoiceField(
        choices=TARGET_ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Optional: choose a role for keyword gap analysis and role matching.',
    )

    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.txt,.docx,image/jpeg,image/png,image/gif,image/webp',
            }),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        name = getattr(f, 'name', '').lower()

        if name.endswith('.doc'):
            raise forms.ValidationError(
                'Legacy .doc format is not supported. Please re-save or export your document as .pdf or .docx.'
            )

        if not any(name.endswith(ext) for ext in ALLOWED_RESUME_EXTENSIONS):
            raise forms.ValidationError(
                'Allowed formats: PDF, TXT, DOCX, or image (JPG, PNG, GIF, WEBP).'
            )

        if f.size > MAX_UPLOAD_SIZE_BYTES:
            raise forms.ValidationError(
                f'File size exceeds the 5MB limit ({f.size / (1024 * 1024):.1f}MB uploaded).'
            )

        return f


class CareerGuidanceForm(forms.Form):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'e.g. Python, machine learning, React, project leadership, data analysis...'
        }),
        label='Skills & interests',
        required=True
    )


class ResumeDraftForm(forms.ModelForm):
    class Meta:
        model = ResumeDraft
        fields = ['title', 'template_name', 'theme_color', 'font_family', 'data']