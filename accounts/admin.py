from django.contrib import admin

# Register your models here.
from accounts.models import User, Seeker, Recruiter, KnowledgeArea, City, Skill, Project

admin.site.register(User)

admin.site.register(Seeker)

admin.site.register(Recruiter)

admin.site.register(City)

admin.site.register(KnowledgeArea)

admin.site.register(Skill)

admin.site.register(Project)