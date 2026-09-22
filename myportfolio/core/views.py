from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum
import json
from .models import (
    PersonalInfo, Experience, Project, Skill,
    Education, Certification, SiteTraffic, ContactMessage
)

def home(request):
    # Track page hits
    today = timezone.now().date()
    traffic, _ = SiteTraffic.objects.get_or_create(date=today)
    traffic.hits += 1
    traffic.save()

    if request.method == 'POST' and 'contact_submit' in request.POST:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'msg': 'Transmission successful. Signal received!'})
            messages.success(request, 'Transmission successful. Signal received!')
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'msg': 'Please supply all required parameters.'}, status=400)
            messages.error(request, 'Please supply all required parameters.')

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

@staff_member_required(login_url='login')
def dashboard(request):
    # 1. Traffic Metrics
    total_hits = SiteTraffic.objects.aggregate(Sum('hits'))['hits__sum'] or 0
    recent_traffic = SiteTraffic.objects.all().order_by('-date')[:7]
    
    # Chronological order for linear graph
    traffic_history = list(reversed(recent_traffic))
    traffic_labels = [entry.date.strftime('%b %d') for entry in traffic_history]
    traffic_data = [entry.hits for entry in traffic_history]

    # 2. Skill Category Distribution for Doughnut / Pie Chart
    backend_count = Skill.objects.filter(category='backend').count()
    frontend_count = Skill.objects.filter(category='frontend').count()
    tools_count = Skill.objects.filter(category='tools').count()
    
    skill_chart_labels = ['Backend & DB', 'Frontend UI', 'Cloud & Tools']
    skill_chart_data = [backend_count, frontend_count, tools_count]

    # 3. Dynamic Profile Health Score Calculation (Max: 100)
    info = PersonalInfo.objects.first()
    experiences = Experience.objects.all()
    projects = Project.objects.all()
    certifications = Certification.objects.all()
    skills = Skill.objects.all()
    education = Education.objects.all()
    contact_messages = ContactMessage.objects.all()[:15]

    score = 0
    score_breakdown = []

    # Bio & Personal Info (20 pts)
    if info and info.about_text and len(info.about_text) > 80:
        score += 10
        score_breakdown.append(("Personal Bio", 10, 10))
    else:
        score_breakdown.append(("Personal Bio", 0, 10))

    if info and info.resume:
        score += 10
        score_breakdown.append(("Resume Attached", 10, 10))
    else:
        score_breakdown.append(("Resume Attached", 0, 10))

    # Experience (20 pts)
    exp_pts = min(experiences.count() * 10, 20)
    score += exp_pts
    score_breakdown.append(("Experience Entries", exp_pts, 20))

    # Projects (25 pts)
    proj_pts = min(projects.count() * 5, 25)
    score += proj_pts
    score_breakdown.append(("Project Artifacts", proj_pts, 25))

    # Certifications & Files (15 pts)
    certs_with_files = sum(1 for c in certifications if c.file)
    cert_pts = min(certs_with_files * 5, 15)
    score += cert_pts
    score_breakdown.append(("Verified Certifications", cert_pts, 15))

    # Skills Matrix (10 pts)
    skill_pts = 10 if skills.count() >= 6 else (skills.count() * 1.5)
    score += int(skill_pts)
    score_breakdown.append(("Technical Skills Depth", int(skill_pts), 10))

    context = {
        'total_hits': total_hits,
        'recent_traffic': recent_traffic,
        'traffic_labels_json': json.dumps(traffic_labels),
        'traffic_data_json': json.dumps(traffic_data),
        'skill_labels_json': json.dumps(skill_chart_labels),
        'skill_data_json': json.dumps(skill_chart_data),
        'profile_score': int(score),
        'score_breakdown': score_breakdown,
        'info': info,
        'experiences': experiences,
        'projects': projects,
        'skills': skills,
        'education': education,
        'certifications': certifications,
        'contact_messages': contact_messages,
    }
    return render(request, 'core/dashboard.html', context)

def custom_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        # Check if request is AJAX/fetch
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

        if is_ajax:
            try:
                data = json.loads(request.body)
            except Exception:
                data = request.POST

            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_staff:
                login(request, user)
                return JsonResponse({'status': 'success', 'redirect_url': '/dashboard/'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'msg': 'ACCESS DENIED // UNAUTHORIZED CIPHER'
                }, status=401)

    return render(request, 'core/login.html')

def tech_stack(request):
    return render(request, 'core/tech_stack.html')