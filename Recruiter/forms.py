from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from .models import JobPost
from accounts.models import User, Recruiter, KnowledgeArea

class JobPostForm(ModelForm):
    class Meta:
        model = JobPost
        fields = ['postion_name', 'job_brief','Responsibilities', 'Requirements_and_skills','soft_skills','city','job_category',
                  'organaization','organaization_logo', 'job_type','contact_email','average_salary']
        labels = {'postion_name': 'Postion name','job_brief':'Job brief','Requirements_and_skills':'Technical skills ', 'city':'City',
                  'job_category':'Job Category','organaization':'organization', 
                  'job_type':'Job type', 'contact_email':'Contact email','average_salary':'Average salary', 'soft_skills':'Soft Skills'}
       

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        self.fields['job_category'].queryset = KnowledgeArea.objects.exclude(name__in=['Soft skills', 'Education'])
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class SearchForSeekers(ModelForm):
    class Meta:
        model = JobPost
        fields = ['postion_name','city']
        labels = {'postion_name': 'Postion name'}
       

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        self.fields['job_category'].queryset = KnowledgeArea.objects.exclude(name__in=['Soft skills', 'Education'])
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
        