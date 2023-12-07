from django.urls import path
from . import views



urlpatterns = [
    path('', views.Recruiter, name='Recruiter'),
    
    path('RecruiterHome/', views.RecruiterHome, name='RecruiterHome'),
    path('RecruiterHome/<str:job_post_id>', views.SearchFromMyJobs, name='search-jobpost'),

    path('RecruiterActivites/', views.RecrutierActivites, name='R-Activites'),
    path('RecruiterViewApplications/', views.RecruiterViewAllApplications, name='all-applications-rec'),
    path('RecruiterViewOffers/', views.RecruiterViewAllOffers, name='all-offers-rec'),

    path('myjobs/', views.userJobPosts, name='myjobs'),

    path('jobpost/<str:pk>/', views.userJobPost, name='user-jobpost'),
    path('create-jobpost/', views.createJobPost, name="create-jobpost"),
    path('update-jobpost/<str:pk>/', views.updateJobPost, name="update-jobpost"),    
    path('delete-jobpost/<str:pk>/', views.deleteJobPost, name="delete-jobpost"), 

   
    path('profile/<str:seeker_id>/<str:job_post_id>/', views.view_seeker_profile, name='view-seeker-profile'),

    path('send_job_offer/<uuid:jobpost_id>/<str:seeker_id>/', views.send_job_offer, name='send_job_offer'),
]
