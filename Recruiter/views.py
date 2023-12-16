from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import TopCandidates

from .forms import JobPostForm
from .models import JobPost, Dictionary, Offers
from accounts.models import User, Recruiter, KnowledgeArea, City, Seeker, Skill
from Seeker.models import Applications
from django.http import JsonResponse


import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor


from django.shortcuts import render

from sentence_transformers import SentenceTransformer, util
import numpy as np


model = SentenceTransformer('stsb-roberta-large')



def get_recruiter_job_posts(recruiter):
    return JobPost.objects.filter(owner=recruiter)


def render_recruiter_template(request, template_name, **context):

    recruiter = request.user.recruiter

    job_posts = get_recruiter_job_posts(recruiter)

    context.update({'job_posts': job_posts})

    return render(request, template_name, context)


def RecrutierActivites(request):

    offers = Offers.objects.filter(jobpost__in=get_recruiter_job_posts(request.user.recruiter))
    
    applications = Applications.objects.filter(jobpost__in=get_recruiter_job_posts(request.user.recruiter))
    
    return render_recruiter_template(request, 'RecrutierActivites.html', offers=offers, applications=applications)


def RecruiterViewAllApplications(request):
    
    applications = Applications.objects.filter(jobpost__in=get_recruiter_job_posts(request.user.recruiter))
    
    return render_recruiter_template(request, 'RecrutierViewAllApplications.html', applications=applications)


def RecruiterViewAllOffers(request):
    
    offers = Offers.objects.filter(jobpost__in=get_recruiter_job_posts(request.user.recruiter))
    
    return render_recruiter_template(request, 'RecrutierViewAllOffers.html', offers=offers)


def send_job_offer(request, jobpost_id, seeker_id):
    jobpost = get_object_or_404(JobPost, id=jobpost_id)
    seeker = get_object_or_404(Seeker, email=seeker_id)

    offer_exists = Offers.objects.filter(seeker=seeker, jobpost=jobpost).exists()
    if not offer_exists:
        offer = Offers(seeker=seeker, jobpost=jobpost, is_new=True)
        offer.save()
        messages.success(request, 'Your proposal has been sent! Check the activities page.')
    else:
        messages.error(request, 'An proposal already exists.')

    return render_seeker_profile(request, seeker, jobpost)


def view_seeker_profile(request, seeker_id, job_post_id):
    seeker = get_object_or_404(Seeker, email=seeker_id)
    job_post = get_object_or_404(JobPost, id=job_post_id)

    return render_seeker_profile(request, seeker, job_post)


def categorize_skills(seeker):
    sk_skills = []
    tech_skills = []

    for skill in seeker.skill_set.all():
        if str(skill.category) == 'Soft skills':
            sk_skills.append(skill)
        else:
            tech_skills.append(skill)

    return sk_skills, tech_skills


def render_seeker_profile(request, seeker, job_post):

    sk_skills, tech_skills = categorize_skills(seeker)

    offer_exists = Offers.objects.filter(seeker=seeker, jobpost=job_post).exists()
    if not offer_exists:
        exist = True
    else:
        exist = False
    
    context = {
        'seeker': seeker,
        'job_post': job_post,
        'sk_skills': sk_skills,
        'tech_skills': tech_skills,
        'projects': seeker.project_set.all(),
        'exist':offer_exists
    }

    return render(request, 'Profile.html', context)

def calculate_similarity_scores(job_post, job_post_embedding, seekers):
    similarity_scores = []
    for seeker in seekers:

        offer_exists = Offers.objects.filter(seeker=seeker, jobpost=job_post).exists()
       
        seeker_skills = " ".join(skill.name for skill in seeker.skill_set.all())

        if seeker.education:
          education= seeker.education
        else:
            education= ""

        if seeker_skills:
            seeker_embeddings = model.encode(seeker_skills+education)
           
            similarity_scores.append((seeker, round(util.pytorch_cos_sim(seeker_embeddings, job_post_embedding)[0][0].item() * 100), seeker.skill_set.all(), offer_exists))
        
            
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            
            Top_seekers=[]
            Remaining_seekers=[]

            for seeker in similarity_scores:
             if seeker[1]>= 70:
                 Top_seekers.append(seeker)
                 continue

             if len(Top_seekers) < 6:
                 Top_seekers.append(seeker)
                 continue
             
             if len(Remaining_seekers) < 30:
                 Remaining_seekers.append(seeker)
                 

             
                        

    return Top_seekers,Remaining_seekers

def RecruiterHome(request):
    if request.method == 'POST':
        position_id = request.POST.get('position')
        city = request.POST.get('city')

        # Retrieve the selected job post using values_list to fetch only required fields
        job_post = JobPost.objects.values_list('Requirements_and_skills', 'soft_skills').get(id=position_id)
        
        # Optimize the database query by using prefetch_related to fetch related skills in advance
        seekers = Seeker.objects.filter(city__name=city, is_active=True).prefetch_related('skill_set')
        
        if not seekers:
            job_posts = request.user.recruiter.jobpost_set.all()
            cities = City.objects.all()
            city_names = cities.values_list('name', flat=True)
            messages.error(request, 'No seekers found in this city, Try another city!')
            context = {
            'city_names': city_names,
            'job_posts': job_posts,
            
            }
            
            return render(request, 'RecruiterHome.html', context)
            

        job_post_merge = job_post[0] + " " + job_post[1]
        job_post_embedding = model.encode(job_post_merge)

        job_post2 = JobPost.objects.filter(id=position_id).first()

        top_seekers1, remaining_seekers1 = calculate_similarity_scores(job_post2, job_post_embedding, seekers)

        cities = City.objects.all()
        city_names = cities.values_list('name', flat=True)
        job_posts = request.user.recruiter.jobpost_set.all()

        context = {
            'city_names': city_names,
            'job_posts': job_posts,
            'similarity_scores': top_seekers1,
            'remaining_seekers':remaining_seekers1,
            'job_post':position_id
        }

        return render(request, 'RecruiterHome.html', context)

    cities = City.objects.all()
    city_names = cities.values_list('name', flat=True)
    job_posts = request.user.recruiter.jobpost_set.all()

    context = {
        'city_names': city_names,
        'job_posts': job_posts
    }

    return render(request, 'RecruiterHome.html', context)

def SearchFromMyJobs(request, job_post_id):
   

    job_post = JobPost.objects.filter(id=job_post_id).first()
    
    if job_post is not None:
        city = job_post.city.name
        
       
        seekers = Seeker.objects.filter(city__name=city, is_active=True).prefetch_related('skill_set')
        if not seekers:
            
            messages.error(request, 'No seekers found in this city. Try to search from home for another cities')
            
            jobposts = request.user.recruiter.jobpost_set.all()
            context = {'jobposts': jobposts} 
            return render(request, 'myjobs.html', context)
        job_post_merge = job_post.Requirements_and_skills + " " + job_post.soft_skills
        job_post_embedding = model.encode(job_post_merge)
        
        top_seekers2, remaining_seekers2 = calculate_similarity_scores(job_post, job_post_embedding, seekers)
        

        cities = City.objects.all()
        city_names = cities.values_list('name', flat=True)
        job_posts = request.user.recruiter.jobpost_set.all()
        recruiter_name = request.user.recruiter.name
        account=request.user.recruiter
      

        context = {
            'city_names': city_names,
            'job_posts': job_posts,
            'similarity_scores': top_seekers2,
            'remaining_seekers' : remaining_seekers2,
            'job_post': job_post_id,
            'UserName': account
        }

        return render(request, 'RecruiterHome.html', context)



@login_required(login_url='login')
def userJobPosts(request):
    jobposts = request.user.recruiter.jobpost_set.all()
    context = {'jobposts': jobposts} 
    return render(request, 'myjobs.html', context)


@login_required(login_url='login')
def userJobPost(request, pk):
    jobpost = get_object_or_404(JobPost, id=pk)
    context = {'jobpost': jobpost} 
    update_top_candidates()
    return render(request, 'jobpost.html', context)



@login_required(login_url='login')
def createJobPost(request):
    form = JobPostForm()

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES)
        if form.is_valid():
            jobpost = form.save(commit=False)
            jobpost.owner = request.user.recruiter
            jobpost.save()

            knowledge_area = get_object_or_404(KnowledgeArea, name='Soft skills')

            tech_skills = jobpost.Requirements_and_skills
            soft_skills = jobpost.soft_skills

            create_skills(extract_skills(tech_skills), jobpost.job_category)
            create_skills(extract_skills(soft_skills), knowledge_area)

            messages.success(request, "Job Post was added successfully")
            return redirect('myjobs')

    context = {'form': form} 
    return render(request, 'jobpost-edit.html', context)


@login_required(login_url='login')
def updateJobPost(request, pk):
    jobpost = JobPost.objects.get(id=pk)
    jobpost3 = JobPost.objects.get(id=pk)
    form = JobPostForm(instance=jobpost)

    if request.method == 'POST':
        form = JobPostForm(request.POST, request.FILES, instance=jobpost)
        if form.is_valid():
            jobpost2 = form.save(commit=False)
            tech_skills = jobpost2.Requirements_and_skills
            soft_skills = jobpost2.soft_skills

            knowledge_area = get_object_or_404(KnowledgeArea, name='Soft skills')

            if jobpost2.Requirements_and_skills != jobpost3.Requirements_and_skills:
                annotations = extract_skills(tech_skills)
                create_skills(annotations, jobpost.job_category)
            
            if jobpost2.soft_skills != jobpost3.soft_skills:
                annotations = extract_skills(soft_skills)
                create_skills(annotations, knowledge_area)


            jobpost2.save()
            messages.success(request, "Job Post was updated successfully")
            return redirect('myjobs')

    context = {'form': form, 'jobpost': jobpost}
    return render(request, 'jobpost-edit.html', context)


@login_required(login_url='login')
def deleteJobPost(request, pk):
    jobpost = get_object_or_404(JobPost, id=pk)
    context = {'object': jobpost} 

    if request.method == 'POST':
        jobpost.delete()
        messages.success(request, "Job Post was deleted successfully")
        return redirect('myjobs')

    return render(request, 'delete-template.html', context)


def extract_skills(job_description):

    # init params of skill extractor
    nlp = spacy.load("en_core_web_lg")
    # init skill extractor
    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

    annotations = skill_extractor.annotate(job_description)
    return annotations


def create_skills(annotations, skill_category):

    for match in annotations['results']['full_matches']:
        name = match['doc_node_value']
        if not Dictionary.objects.filter(name=name).exists():
            name = name.lower()
            skill = Dictionary.objects.create(skill_category=skill_category, name=name)

    for match in annotations['results']['ngram_scored']:
        name = match['doc_node_value']
        if not Dictionary.objects.filter(name=name).exists():
            name = name.lower()
            skill = Dictionary.objects.create(skill_category=skill_category, name=name)

def Recruiter(request):
    return render(request, 'Recruiter/RecruiterHome.html')


def toggle_active(request):
    if request.method == 'POST':
        job_post_id = request.POST.get('job_post_id')
        is_active = request.POST.get('is_active')

        # Perform the necessary logic to update the `is_active` value for the job post
        # Here's an example of updating the `is_active` value in the database

        # Assuming you have a JobPost model
        from .models import JobPost
        job_post = JobPost.objects.get(id=job_post_id)
        job_post.is_active = is_active == 'true'
        job_post.save()

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})

    # Return a JSON response indicating failure if the request method is not POST
    return JsonResponse({'status': 'failure'}, status=400)

def calculate_similarity_scores_r(job_post_embedding, seekers):
    similarity_scores = []
    for seeker in seekers:
        seeker_skills = " ".join(skill.name for skill in seeker.skill_set.all())
        if seeker.education:
          education= seeker.education
        else:
            education= ""

        if seeker_skills:
            seeker_embeddings = model.encode(seeker_skills+education)
            similarity_scores.append((seeker, round(util.pytorch_cos_sim(seeker_embeddings, job_post_embedding)[0][0].item() * 100), seeker.skill_set.all()))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    return similarity_scores

def update_top_candidates():
    seekers = Seeker.objects.filter(is_active=True)
    job_posts = JobPost.objects.filter(is_active=True)

    for job_post in job_posts:
        top_candidates = []

        if job_post.Requirements_and_skills is None or job_post.soft_skills is None:
            continue

        job_post_merge = job_post.Requirements_and_skills + " " + job_post.soft_skills
        job_post_embedding = model.encode(job_post_merge)

        similarity_scores = calculate_similarity_scores_r(job_post_embedding, seekers)
        top_candidates = [seeker for seeker, _, _ in similarity_scores[:5]]  # Get top 5 candidates

        # Create or update TopCandidates instance for the job post
        top_candidates_instance, _ = TopCandidates.objects.get_or_create(job_post=job_post)
        top_candidates_instance.seekers.set(top_candidates)
        TopCandidates.objects.exclude(job_post__in=job_posts).delete()