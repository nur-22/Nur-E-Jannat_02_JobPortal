from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    USER_TYPES = [
        ('Recruiter', 'Recruiter'),
        ('Job Seeker', 'Job Seeker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    def __str__(self):
        return self.user.username


class RecruiterProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)
    company_description = models.TextField()

    def __str__(self):
        return self.company_name


class JobSeekerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    skills = models.TextField()
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.user_profile.user.username


class Job(models.Model):
    recruiter = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    number_of_openings = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    description = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.job_seeker.user.username + " - " + self.job.title)