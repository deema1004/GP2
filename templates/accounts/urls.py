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

    path('account/', views.userAccount, name='account'),
    path('edit-account/', views.editAccount, name="edit-account"),
    path('add-skill/', views.AddSkill, name="add-skill"),
    
]