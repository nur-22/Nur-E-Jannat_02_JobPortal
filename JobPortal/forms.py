from django import forms
from django.contrib.auth.models import User
from .models import (UserProfile, Job, RecruiterProfile, JobSeekerProfile)


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    display_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    user_type = forms.ChoiceField(choices=[('Recruiter', 'Recruiter'), ('Job Seeker', 'Job Seeker')])

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'number_of_openings', 'category', 'description', 'skills']

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'company_description']


class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'resume']