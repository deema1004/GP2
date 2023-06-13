from django.urls import path
from . import views



urlpatterns = [
    path('', views.Recruiter, name='Recruiter'),
    
    path('myjobs/', views.userJobPosts, name='myjobs'),

    path('jobpost/<str:pk>/', views.userJobPost, name='user-jobpost'),

    path('create-jobpost/', views.createJobPost, name="create-jobpost"),
    path('update-jobpost/<str:pk>/', views.updateJobPost, name="update-jobpost"),    
    path('delete-jobpost/<str:pk>/', views.deleteJobPost, name="delete-jobpost"), 
]
