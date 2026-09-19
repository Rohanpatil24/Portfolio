from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Sum
from .models import PersonalInfo, Experience, Project, Skill, Education, Certification, SiteTraffic

def home(request):
    # Track daily traffic
    today = timezone.now().date()
    traffic, created = SiteTraffic.objects.get_or_create(date=today)
    traffic.hits += 1
    traffic.save()

    context = {
        'info': PersonalInfo.objects.first(),
        'experiences': Experience.objects.all().order_by('order'),
        'projects': Project.objects.all().order_by('order'),
        'backend_skills': Skill.objects.filter(category='backend'),
        'frontend_skills': Skill.objects.filter(category='frontend'),
        'tools_skills': Skill.objects.filter(category='tools'),
        'education': Education.objects.all(),
        'certifications': Certification.objects.all(),
    }
    return render(request, 'core/index.html', context)

@staff_member_required(login_url='login')
def dashboard(request):
    total_hits = SiteTraffic.objects.aggregate(Sum('hits'))['hits__sum'] or 0
    recent_traffic = SiteTraffic.objects.all().order_by('-date')[:7]
    
    context = {
        'total_hits': total_hits,
        'recent_traffic': recent_traffic,
        'info': PersonalInfo.objects.first(),
        'experiences': Experience.objects.all(),
        'projects': Project.objects.all(),
        'skills': Skill.objects.all(),
        'education': Education.objects.all(),
        'certifications': Certification.objects.all(),
    }
    return render(request, 'core/dashboard.html', context)