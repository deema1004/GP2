from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from accounts.models import Seeker
from Recruiter.models import JobPost
# Create your models here.

validate_year_month_format = RegexValidator(
    regex=r'^\d{4}-\d{2}$',
    message='Format must be YYYY-MM',
    code='invalid_year_month'
)

class Applications(models.Model):
    seeker = models.ForeignKey(Seeker, on_delete=models.SET_NULL,null=True, blank=True)
    jobpost = models.ForeignKey(JobPost,on_delete=models.SET_NULL,null=True, blank=True)
    is_new = models.BooleanField(default=True)
    month_year = models.CharField(
        max_length=7,
        validators=[validate_year_month_format],
        default=timezone.localdate().strftime('%Y-%m'),
        help_text="Format: YYYY-MM"
    )
    def __str__(self):
        return str(self.jobpost)