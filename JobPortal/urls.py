from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('jobs/post/', views.job_post_view, name='job_post'),
    path('jobs/search/', views.job_search_view, name='job_search'),
    path('jobs/apply/<int:job_id>/', views.apply_job_view, name='apply_job'),
    path('profile/', views.profile_view, name='profile'),
    path('jobs/matches/', views.skill_match_view, name='skill_matches'),

    path('jobs/edit/<int:job_id>/', views.edit_job_view, name='edit_job'),
    path('jobs/delete/<int:job_id>/', views.delete_job_view, name='delete_job'),
]