from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from .models import User, Seeker, Recruiter, Skill, Project


class SignupForm(UserCreationForm):
   
    User_Type = forms.ChoiceField(choices=[('Seeker','Seeker'),('Recruiter','Recruiter')])
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']
        labels = {'first_name': 'Name',}

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})



class SeekerAccountForm(ModelForm):
    class Meta:
        model = Seeker
        fields = ['name', 'email', 'username', 'cv',
                  'city', 'short_intro','bio','profile_image',
                  'social_github', 'social_linkedin', 'social_twitter',
                  'social_website']
       
        
        

    def __init__(self, *args, **kwargs):
        super(SeekerAccountForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class RecruiterAccountForm(ModelForm):
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'username','organization',
                  'city', 'short_intro','bio','profile_image',
                  'social_github', 'social_linkedin', 'social_twitter',
                  'social_website']
       

    def __init__(self, *args, **kwargs):
        super(RecruiterAccountForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})




class AddSkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ['name','category']
        labels = {'name': 'Name','category':'Category'}


    def __init__(self, *args, **kwargs):
        super(AddSkillForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
           
    
    
class projectForm(ModelForm):
    class Meta:
        model = Project
        fields =['name','description','link']

        
    def __init__(self, *args, **kwargs):
        super(projectForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})