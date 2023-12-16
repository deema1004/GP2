from django.urls import path
from . import views

urlpatterns = [
    path('', views.Seeker ,  name='Seeker'),

    path('SeekerHome/', views.SeekerHome, name='SeekerHome'),


    path('delete-skill/<str:pk>/',views.deleteSkill,name='delete-skill'),

    path('jobpost/<str:job_post_id>/<str:seeker_id>', views.SeekerViewJobPost, name='seeker-jobpost'),
    path('toggle-active/', views.toggle_active1, name='toggle-active'),

    path('Application/<str:jobpost_id>/<str:seeker_id>/', views.SeekerApplication, name='Apply'),

    path('SeekerActivites/', views.SeekerActivites, name='S-Activites'),
    path('SeekerViewApplications/', views.SeekerViewAllApplications, name='all-applications-sek'),
    path('SeeekerViewOffers/', views.SeekerViewAllOffers, name='all-offers-sek'),
]