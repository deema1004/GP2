from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    
    path('', views.main ,name='main'),
    path('signup/', views.userSignUp, name='signup'),
    path('login/', views.userLogin, name='login'),
    path('logout/', views.userLogout, name='logout'),
    path('login-after-active/', views.userLoginActivate, name='login-after-active'),
    
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    

    path('profile/', views.userProfile, name='profile'),

    path('notofications/', views.Notofications, name='notofications'),
    
    path('navbar/', views.navbar ,name='navbar'),

    path('account/', views.userAccount, name='account'),
    path('edit-account/', views.editAccount, name="edit-account"),
    path('add-skill/', views.AddSkill, name="add-skill"),
    path('create-project/',views.createProject,name='create-project'),
    path('update-project/<str:pk>/',views.updateProject,name='update-project'),
    path('delete-project/<str:pk>/',views.deleteProject,name='delete-project'),
    path('mark-offer-as-seen/', views.mark_offer_as_seen, name='mark_offer_as_seen'),
    path('mark-application-as-seen/', views.mark_application_as_seen, name='mark_application_as_seen'),
    
    
]