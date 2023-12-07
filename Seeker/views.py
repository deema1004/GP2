from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse

from accounts.models import City, Seeker, Skill
from Recruiter.models import JobPost, Offers
from .models import Applications

from django.shortcuts import render

from django.db.models import Q

from sentence_transformers import SentenceTransformer, util
import numpy as np


model = SentenceTransformer('stsb-roberta-large')


def SeekerActivites(request):
    seeker = request.user.seeker

    offers = Offers.objects.filter(seeker=seeker)
    applications = Applications.objects.filter(seeker=seeker)

    context = {
        'offers': offers,
        'applications': applications
    }

    return render(request, 'SeekerActivites.html', context)

def SeekerViewAllApplications(request):
    
    applications = Applications.objects.filter(seeker=request.user.seeker)
    
    context = {'applications':applications}
    
    return render(request, 'SeekerViewAllApplications.html', context)


def SeekerViewAllOffers(request):
    
    offers = Offers.objects.filter(seeker=request.user.seeker)

    context = {'offers':offers}
    return render(request, 'SeekerViewAllOffers.html', context)



def SeekerApplication(request, jobpost_id, seeker_id):
    jobpost = get_object_or_404(JobPost, id=jobpost_id)
    
    seeker = get_object_or_404(Seeker, email=seeker_id)

    application_exists = Applications.objects.filter(seeker=seeker, jobpost=jobpost).exists()
    if not application_exists:
        application = Applications(seeker=seeker, jobpost=jobpost, is_new=True)
        application.save()
        messages.success(request, 'Your application has been sent! Check the activities page.')
    else:
        messages.error(request, 'An application already exists.')
        
    context = {
        'jobpost': jobpost,
        'seeker_id':seeker_id
    }
    return render(request, 'jobpost-seeker-view.html', context)

    


def SeekerViewJobPost(request, job_post_id, seeker_id):
    jobpost = get_object_or_404(JobPost, id=job_post_id)
    seeker = get_object_or_404(Seeker, email=seeker_id)

    application_exists = Applications.objects.filter(seeker=seeker, jobpost=jobpost).exists()
    if not application_exists:
        exist = True
    else:
        exist = False
       
    context = {'jobpost': jobpost, 'seeker_id':seeker_id,'exist':exist } 
    return render(request, 'jobpost-seeker-view.html', context)

def calculate_similarity_scores(job_posts, seeker):
    

    similarity_scores = []
    skills = " ".join(skill.name for skill in seeker.skill_set.all())
    seeker_embeddings = model.encode(skills)

    for job in job_posts:
            application_exists = Applications.objects.filter(seeker=seeker, jobpost=job).exists()
            print(application_exists)
            job_post_merge = job.Requirements_and_skills + " " + job.soft_skills
            job_post_embedding = model.encode(job_post_merge)
            similarity_scores.append((round(util.pytorch_cos_sim(seeker_embeddings, job_post_embedding)[0][0].item() * 100), job, application_exists ))
    
    similarity_scores = sorted(similarity_scores, key=lambda x: x[0], reverse=True)
  
            
    Top_posts=[]
    Remaining_posts=[]

    for seeker in similarity_scores:
             if seeker[0]>= 70:
                 Top_posts.append(seeker)
                 continue

             if len(Top_posts) < 6:
                 Top_posts.append(seeker)
                 continue
             
             if len(Remaining_posts) < 30:
                 Remaining_posts.append(seeker)
                 

    return Top_posts, Remaining_posts

def SeekerHome(request):
   
    if request.method == 'POST':
        
        Jobtype = request.POST.get('Jobtype')
        city = request.POST.get('city')
        job_posts = JobPost.objects.filter(Q(job_type__name=Jobtype) & Q(city__name=city) & Q(is_active=True))

        seeker=request.user.seeker
       


        # job_post_merge = job_post[0] + " " + job_post[1]
        # job_post_embedding = model.encode(job_post_merge)

        Top_posts, Remaining_posts = calculate_similarity_scores(job_posts, seeker)

        cities = City.objects.all()
        city_names = cities.values_list('name', flat=True)
        
        
        context = {
            'city_names': city_names,
            'job_posts': job_posts,
            'similarity_scores': Top_posts,
            'Remaining_posts': Remaining_posts,
            'seeker_email':seeker.email
            
            
        }


        return render(request, 'SeekerHome.html', context)
  
    cities = City.objects.all()
    city_names = cities.values_list('name', flat=True)
    job_posts = JobPost.objects.all()

    context = {
        'city_names': city_names,
        'job_posts': job_posts,
        
    }

    return render(request, 'SeekerHome.html', context)

