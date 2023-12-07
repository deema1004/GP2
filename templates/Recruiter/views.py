from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .forms import JobPostForm
from .models import JobPost, Dictionary
from accounts.models import User, Recruiter, KnowledgeArea

import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor

@login_required(login_url='login')
def userJobPosts(request):
    jobposts = request.user.recruiter.jobpost_set.all()
    context = {'jobposts': jobposts} 
    return render(request, 'myjobs.html', context)


@login_required(login_url='login')
def userJobPost(request, pk):
    jobpost = get_object_or_404(JobPost, id=pk)
    context = {'jobpost': jobpost} 
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
