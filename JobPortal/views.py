from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models

from .models import (UserProfile, Job, JobApplication, JobSeekerProfile, RecruiterProfile)
from .forms import (RegisterForm, LoginForm, JobForm, RecruiterProfileForm, JobSeekerProfileForm)

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'])

            UserProfile.objects.create(
                user=user,
                display_name=form.cleaned_data['display_name'],
                user_type=form.cleaned_data['user_type'])

            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')

            messages.error(request, 'Invalid username or password.')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required(login_url='login')
def dashboard_view(request):

    if request.user.is_superuser:
        return render(request, 'dashboard.html', {'is_admin': True})

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username, 'user_type': 'Job Seeker'}
    )

    context = {'profile': profile, 'is_admin': False}

    if profile.user_type == 'Recruiter':
        recruiter_jobs = Job.objects.filter(recruiter=profile).order_by('-created_at')
        context['recruiter_jobs'] = recruiter_jobs

    else:

        query = request.GET.get('q', '')
        jobs = Job.objects.all().order_by('-created_at')

        if query:
            jobs = jobs.filter(
                models.Q(title__icontains=query) |
                models.Q(category__icontains=query) |
                models.Q(skills__icontains=query)
            )

        context['query'] = query
        context['jobs'] = jobs

        try:
            seeker_profile = profile.jobseekerprofile
            user_skills = seeker_profile.skills.split(',')

        except JobSeekerProfile.DoesNotExist:
            user_skills = []

        matched_jobs = []

        for job in Job.objects.all():

            matching_skills = []

            for skill in job.skills.split(','):

                for user_skill in user_skills:

                    if skill.strip().lower() == user_skill.strip().lower():
                        matching_skills.append(skill.strip())
                        break

            if matching_skills:
                matched_jobs.append({
                    'job': job,
                    'matching_skills': matching_skills
                })

        context['matched_jobs'] = matched_jobs
        context['user_skills'] = user_skills

    return render(request, 'dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def job_post_view(request):
    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type != 'Recruiter':
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = profile
            job.save()

            messages.success(request, 'Job posted successfully!')
            return redirect('dashboard')

    else:
        form = JobForm()

    return render(request, 'job_post.html', {'form': form})


@login_required(login_url='login')
def job_search_view(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all().order_by('-created_at')

    if query:
        jobs = jobs.filter(
            models.Q(title__icontains=query) |
            models.Q(category__icontains=query) |
            models.Q(skills__icontains=query))

    return render(request, 'job_search.html', {'jobs': jobs, 'query': query})


@login_required(login_url='login')
def apply_job_view(request, job_id):
    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type != 'Job Seeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id)

    application, created = JobApplication.objects.get_or_create(job=job, job_seeker=profile)

    if created:
        messages.success(request, 'You applied successfully!')
    else:
        messages.info(request, 'You have already applied for this job.')

    return redirect('dashboard')


@login_required(login_url='login')
def profile_view(request):
    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type == 'Recruiter':
        recruiter_profile, _ = RecruiterProfile.objects.get_or_create(
            user_profile=profile,
            defaults={'company_name': '', 'company_description': ''})

        if request.method == 'POST':
            form = RecruiterProfileForm(request.POST, instance=recruiter_profile)

            if form.is_valid():
                form.save()
                messages.success(request, 'Profile saved successfully!')
                return redirect('dashboard')

        else:
            form = RecruiterProfileForm(instance=recruiter_profile)

        return render(request, 'recruiter_profile.html', {'form': form})

    seeker_profile, _ = JobSeekerProfile.objects.get_or_create(
        user_profile=profile, 
        defaults={'skills': ''}
        )

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=seeker_profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile saved successfully!')
            return redirect('dashboard')

    else:
        form = JobSeekerProfileForm(instance=seeker_profile)

    return render(request, 'jobseeker_profile.html', {'form': form})


@login_required(login_url='login')
def skill_match_view(request):
    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type == 'Job Seeker':
        try:
            seeker_profile = profile.jobseekerprofile

            seeker_skills = [skill.strip().lower()
                for skill in seeker_profile.skills.split(',')
                if skill.strip()]

        except JobSeekerProfile.DoesNotExist:
            seeker_skills = []

        matched_jobs = []

        for job in Job.objects.all():
            required_skills = [skill.strip().lower()
                for skill in job.skills.split(',')
                if skill.strip()]

            matching_skills = [skill for skill in required_skills
                if skill in seeker_skills]

            if matching_skills:
                matched_jobs.append({'job': job, 'matching_skills': matching_skills})

        return render(
            request, 
            'skill_matches.html', 
            {'matched_jobs': matched_jobs, 'user_skills': seeker_skills}
            )

    else:
        jobs = Job.objects.filter(recruiter=profile)

        return render(request, 'skill_matches.html', {'recruiter_jobs': jobs})

@login_required(login_url='login')
def edit_job_view(request, job_id):

    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type != 'Recruiter':
        messages.error(request, 'Only recruiters can edit jobs.')
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id, recruiter=profile)

    if request.method == 'POST':

        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()

            messages.success(request, 'Job updated successfully!')

            return redirect('dashboard')

    else:
        form = JobForm(instance=job)

    return render(request, 'job_edit.html', {'form': form, 'job': job})

@login_required(login_url='login')
def delete_job_view(request, job_id):

    if request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.user_type != 'Recruiter':
        messages.error(request, 'Only recruiters can delete jobs.')
        return redirect('dashboard')

    if request.method == 'POST':

        job = get_object_or_404(Job, id=job_id, recruiter=profile)
        job.delete()
        messages.success(request, 'Job deleted successfully!')

    return redirect('dashboard')