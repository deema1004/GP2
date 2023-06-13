from django.db import models
from accounts.models import Recruiter, KnowledgeArea, City
import uuid

class JobType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
# Create your models here.
class JobPost(models.Model):
    owner = models.ForeignKey(Recruiter, on_delete=models.CASCADE,null=True, blank=True)
    postion_name = models.CharField(max_length=200, blank=False, null=False)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=False)
    job_category = models.ForeignKey(KnowledgeArea, on_delete=models.SET_NULL, null=True, blank=False)
    organaization = models.CharField(max_length=200, blank=False, null=False)
    job_type= models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True, blank=False)
    organaization_logo =models.ImageField(null=True, blank=True, default='jobpost.jpg') 
    job_brief = models.CharField(max_length=200, blank=False, null=True)
    Requirements_and_skills = models.TextField(null=True, blank=False)
    soft_skills = models.TextField(null=True, blank=False)
    Responsibilities = models.TextField(null=True, blank=False)
    contact_email = models.EmailField(null=True, blank=False)
    average_salary = models.IntegerField(null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, 
                          primary_key=True, editable=False)
    
                        

    def __str__(self):
        return self.postion_name 
    
class SkillCategory(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
# Create your models here.
class Dictionary(models.Model):
    name = models.CharField(max_length=200, blank=False, null=True)
    skill_category = models.ForeignKey(KnowledgeArea, on_delete=models.SET_NULL, null=True, blank=False)
   
     
    def __str__(self):
        return self.name