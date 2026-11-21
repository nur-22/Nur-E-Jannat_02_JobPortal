from django.contrib import admin
from .models import (UserProfile, RecruiterProfile, JobSeekerProfile, Job, JobApplication)

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(RecruiterProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(Job)
admin.site.register(JobApplication)