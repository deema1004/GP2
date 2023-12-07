from django.db import models
from django.utils import timezone

from accounts.models import Seeker
from Recruiter.models import JobPost
# Create your models here.
class Applications(models.Model):
    seeker = models.ForeignKey(Seeker, on_delete=models.SET_NULL,null=True, blank=True)
    jobpost = models.ForeignKey(JobPost,on_delete=models.SET_NULL,null=True, blank=True)
    is_new = models.BooleanField(default=True)
    def __str__(self):
        return str(self.jobpost)