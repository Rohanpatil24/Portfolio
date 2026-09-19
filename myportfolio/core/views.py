from django.shortcuts import render
from .models import PersonalInfo, Experience, Project, Skill, Education

def home(request):
    context = {
        # Grab the first record for personal info
        'info': PersonalInfo.objects.first(),
        'experiences': Experience.objects.all(),
        'projects': Project.objects.all(),
        'backend_skills': Skill.objects.filter(category='backend'),
        'frontend_skills': Skill.objects.filter(category='frontend'),
        'tools_skills': Skill.objects.filter(category='tools'),
        'education': Education.objects.filter(is_certification=False),
        'certifications': Education.objects.filter(is_certification=True),
    }
    return render(request, 'core/index.html', context)