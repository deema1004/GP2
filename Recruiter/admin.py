from django.contrib import admin

# Register your models here.
from Recruiter.models import JobPost, JobType, Dictionary, Offers

admin.site.register(JobPost)

admin.site.register(JobType)

admin.site.register(Dictionary)

admin.site.register(Offers)