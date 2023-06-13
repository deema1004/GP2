from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .forms import SignupForm, SeekerAccountForm, RecruiterAccountForm, AddSkillForm
from .models import User, Seeker, Recruiter, Skill, KnowledgeArea
from Recruiter.models import Dictionary
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError
from email_validator import validate_email
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from .tokens import account_activation_token
import spacy
import chardet
import docx2txt
import textract
import re


def userSignUp(request):

    page = 'register'
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)
        email = request.POST.get('email')
        
        if form.is_valid():

         if not validate_email(email):
                 messages.error(request,
                                 'Enter a valid email address')
         else:
                 
            user = form.save(commit=False)
            user.email = user.email.lower()
            #user.email_verified = True
            UserType= request.POST.get('User_Type')
            

            if(UserType=='Seeker'):
               user.is_Seeker= True
            else:
                user.is_Recruiter = True

            user.save()
            
            if(UserType=='Seeker'):
               seeker = Seeker.objects.create(user=user,
                                              username=user.username,
                                              email=user.email,
                                              name=user.first_name,
                                              )
            else:
                recruiter = Recruiter.objects.create(user=user,
                                                     username=user.username,
                                                     email=user.email,
                                                     name=user.first_name,)

            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('login')
            

        else:
            messages.error(
                request, 'An error has occurred during registration')
        


    context = {'page': page, 'form': form}
    return render(request, 'signup_login.html', context)


def userLogout(request):
    logout(request)
    messages.info(request ,'User was logged out!')
    return redirect('login')

nlp = spacy.load('en_core_web_lg')


def tokenize_cv(cv_file):

    file_extension = cv_file.name.split('.')[-1]

    if file_extension == 'docx':
        cv_text = docx2txt.process(cv_file)

    elif file_extension == 'txt':
        cv_text = cv_file.read().decode('utf-8')

    elif file_extension == 'rtf':
        cv_text = textract.process(cv_file).decode('utf-8')

    else:
        raise ValueError('Unsupported file type')
        
    cv_text = cv_text.lower()

    cv_text = re.sub(r'\d+','',cv_text)
    
    doc = nlp(cv_text)
    
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    entities = [entity.text.lower() for entity in doc.ents if entity.label_ == 'PRODUCT']
    
    return tokens + entities


def preprocess_skills(skill_dict):

    return {major: {skill.lower() for skill in skills if skill} for major, skills in skill_dict.items()}


def extract_skills(tokens, seeker):


    skills = Dictionary.objects.all()

    matches = []

    # Get the existing skills 
    existing_skills = Skill.objects.filter(owner=seeker)

    # Delete the existing skills
    existing_skills.delete()


    for skill in skills:
        for prev ,cur, nxt in zip (tokens, tokens [1:],tokens[2:]):

            twowordtoken= cur+" "+nxt
            threewordtoken= prev+" "+cur+" "+nxt

            if twowordtoken==skill.name:
             if not Skill.objects.filter(name=skill.name, owner=seeker).exists():
                skill = Skill.objects.create(owner=seeker, category=skill.skill_category , name=skill.name)
            
            elif threewordtoken==skill.name:
                matches.append(skill)
                if not Skill.objects.filter(name=skill.name, owner=seeker).exists():
                    skill = Skill.objects.create(owner=seeker, category=skill.skill_category , name=skill.name)
            
            elif cur==skill.name:
                matches.append(skill)
                if not Skill.objects.filter(name=skill.name, owner=seeker).exists():
                    skill = Skill.objects.create(owner=seeker, category=skill.skill_category , name=skill.name)
                

    return matches



def activate(request, uidb64, token):

    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified= True
        user.save()


        messages.success(request, "Thank you, your account is now activated. Try to login")
        return redirect('login-after-active')
    
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('login')


def activateEmail(request, user, to_email):

    mail_subject = "Activate your user account."

    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email} inbox and click on \
                received activation link to confirm and complete the registration. \n Note: Check your spam folder.')
    
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')



def userLogin(request):

    page = 'login'
    
    if request.user.is_authenticated:
       return redirect('main')

    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:

            messages.error(request, 'Email does not exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        user2 = User.objects.get(email=email)
        if user2.email_verified:
            if user is not None:
                login(request, user)#create session
                return redirect('account')

            else:
                messages.error(request, 'Email OR password is incorrect')
        else:
            messages.error(request, 'check your email inbox to activate your account')

    return render(request, 'signup_login.html')


@login_required(login_url='login')
def userAccount(request):

    skills = []  

    if request.user.is_Seeker:
       account=request.user.seeker
       skills = account.skill_set.all()
       category = get_object_or_404(KnowledgeArea, name='Soft skills')
      

    

    elif request.user.is_Recruiter:
        account=request.user.recruiter

    context = {'account': account, 'skills':skills, 'sk':category}
    return render(request, 'account.html', context)

def userLoginActivate(request):

    page = 'login'
    
    if request.user.is_authenticated:
       return redirect('main')

    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:

            messages.error(request, 'Email does not exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        user2 = User.objects.get(email=email)
        if user2.email_verified:
            if user is not None:
                login(request, user)#create session
                return redirect('edit-account')

            else:
                messages.error(request, 'Email OR password is incorrect')
        else:
            messages.error(request, 'check your email inbox to activate your account')

    return render(request, 'signup_login.html')


@login_required(login_url='login')
def editAccount(request):

    if request.user.is_Seeker:
        seeker = request.user.seeker
        form = SeekerAccountForm(instance=seeker)

    elif request.user.is_Recruiter:
        recruiter = request.user.recruiter
        form = RecruiterAccountForm(instance=recruiter)

    AllSkills = []

    if request.method == 'POST':
        if request.user.is_Seeker:
            form = SeekerAccountForm(request.POST, request.FILES, instance=seeker)
            if form.is_valid():
                # Validate file extension
               
                file = request.FILES.get('cv', None)
                if file:
                    try:
                        # Validate the file extension
                        validate_word_or_text_file(file)
                        tokens = tokenize_cv(file)
                        
                        extract_skills(tokens, seeker)
                    except ValidationError as e:
                        form.add_error('cv', e)
                        messages.error(request, 'the cv format is not accepted, Try (.docx , .txt , .rtf)')
                        return render(request, 'account-edit.html', {'form': form})
                
                form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('account')
            
        elif request.user.is_Recruiter:
            form = RecruiterAccountForm(request.POST, request.FILES, instance=recruiter)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('account')

    context = {'form': form}
    
    if request.user.is_Seeker and seeker is not None:
        context['cv_skills'] = AllSkills

    return render(request, 'account-edit.html', context)

def validate_word_or_text_file(file):

    ext = file.name.split('.')[-1]
    if ext not in ['docx', 'txt', 'rtf']:
        raise ValidationError(f'File type "{ext}" is not supported.')



def updateUser(created,sender,instance,**kwargs):

    SeekerOrProvider=instance
    user=SeekerOrProvider.user

    if created == False:
        user.first_name = SeekerOrProvider.name
        user.username = SeekerOrProvider.username
        user.email = SeekerOrProvider.email
        user.is_active = SeekerOrProvider.is_active
        user.save()

post_save.connect(updateUser,sender=Seeker)
post_save.connect(updateUser,sender=Recruiter)


@login_required(login_url='login')
def AddSkill(request):

    form = AddSkillForm()

    if request.method == 'POST':
        form = AddSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = request.user.seeker
            name = skill.name
            category = skill.category
            if not Skill.objects.filter(name=skill.name,owner=request.user.seeker).exists():
                skill.save()
                if not Dictionary.objects.filter(name=skill.name).exists():
                    skill = Dictionary.objects.create(skill_category=category, name=name.lower())
            

                messages.success(request, "Skill was added successfully")
                return redirect('account')
            else:
                messages.error(request, "Skill already exists")

    context = {'form': form} 
    return render(request, 'add-skill.html', context)

def accounts(request):
    return render(request, 'accounts/accountsHome.html')

def main(request):
    return render(request, 'main.html')

def SignUpType(request):
	return render(request,'signup_login.html')

def userProfile(request):
	return render(request,'profile.html')

def Profile(request):
	return render(request,'signup_login.html')








