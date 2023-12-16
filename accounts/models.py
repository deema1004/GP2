import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False) 
    is_Seeker = models.BooleanField(default=False)
    is_Recruiter = models.BooleanField(default=False)

    def get_profile_image(self):
        if self.is_Seeker:
            try:
                seeker = self.seeker
            except ObjectDoesNotExist:
                return None
            return seeker.profile_image

        elif self.is_Recruiter:
            try:
                recruiter = self.recruiter
            except ObjectDoesNotExist:
                return None
            return recruiter.profile_image

        return None

    @property
    def profile_image(self):
        return self.get_profile_image()
    
    def is_online(self):
        from chat.models import UserOnlineStatus
        obj = UserOnlineStatus.objects.filter(user=self).last()
        if obj is None:
            return False
        return obj.online


class City(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class KnowledgeArea(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Seeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    cv = models.FileField(upload_to='uploads/', null=True, blank=False)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=False)
    age = models.IntegerField(range(1, 75),null=True, blank=True)
    short_intro = models.CharField(max_length=200, null=True, blank=True)
    education = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image =models.ImageField(null=True, blank=True, default='user-default.png') 
    social_github = models.CharField(max_length=200, null=True, blank=True)
    social_twitter = models.CharField(max_length=200, null=True, blank=True)
    social_linkedin = models.CharField(max_length=200, null=True, blank=True)
    social_website = models.CharField(max_length=200, null=True, blank=True)
    is_active=models.BooleanField(default=True)
    numPOffers=models.IntegerField(range(1, 200), null=True)

    def __str__(self):
        return self.user.username
    
class Skill(models.Model):
    owner = models.ForeignKey(Seeker, on_delete=models.CASCADE,null=True, blank=True)
    category = models.ForeignKey(KnowledgeArea, on_delete=models.CASCADE, null=True, blank=False)
    name = models.CharField(max_length=200, blank=False, null=False)

    def __str__(self):
        return str(self.name)

class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=500, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True,blank=False)
    organization = models.CharField(max_length=200, null=True, blank=False)
    short_intro = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image =models.ImageField(null=True, blank=True, upload_to='images/profile/',  default='user-default.png') 
    social_github = models.CharField(max_length=200, null=True, blank=True)
    social_twitter = models.CharField(max_length=200, null=True, blank=True)
    social_linkedin = models.CharField(max_length=200, null=True, blank=True)
    social_website = models.CharField(max_length=200, null=True, blank=True)
    is_active=models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username

class Project(models.Model):
    owner = models.ForeignKey(Seeker, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(null=True,blank=True)
    link = models.CharField(max_length=200, null=True, blank=True)
    created = models.TextField(null=True,blank=True)
    id=models.UUIDField(default= uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return str(self.name)
    
class NumberOfViews(models.Model):
    count=models.IntegerField(blank=False, default=0)

    def __str__(self):
        return str(self.count)