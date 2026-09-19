from django.shortcuts import render
from .models import PersonalInfo, Experience, Project, Skill, Education, Certification

def home(request):
    context = {
        'info': PersonalInfo.objects.first(),
        'experiences': Experience.objects.all(),
        'projects': Project.objects.all(),
        'backend_skills': Skill.objects.filter(category='backend'),
        'frontend_skills': Skill.objects.filter(category='frontend'),
        'tools_skills': Skill.objects.filter(category='tools'),
        'education': Education.objects.all(),
        'certifications': Certification.objects.all(),
    }
    return render(request, 'core/index.html', context)