from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def Seeker(request):
    return render(request, 'Seeker/SeekerHome.html')