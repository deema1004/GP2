from django import template
from Recruiter.models import Offers, JobPost
from accounts.models import User
from Seeker.models import Applications

register = template.Library()


@register.filter
def has_new_offers(seeker_email):
    return Offers.objects.filter(seeker__email=seeker_email, is_new=True).exists()

# Custom filter for recruiters
@register.filter
def has_new_applications(recruiter_email):
    recruiter = User.objects.get(email=recruiter_email)
    return Applications.objects.filter(jobpost__owner__user=recruiter, is_new=True).exists()
