from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum
import json
import logging
from .models import (
    PersonalInfo, Experience, Project, Skill,
    Education, Certification, SiteTraffic, ContactMessage
)
from .pipeline import generate_portfolio_dataset

logger = logging.getLogger(__name__)

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
        'projects': Project.objects.prefetch_related('images').all(),
        'backend_skills': Skill.objects.filter(category='backend'),
        'frontend_skills': Skill.objects.filter(category='frontend'),
        'tools_skills': Skill.objects.filter(category='tools'),
        'education': Education.objects.all(),
        'certifications': Certification.objects.all(),
    }
    return render(request, 'core/index.html', context)

# core/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from .models import PersonalInfo, Experience, Project, Skill, Education, Certification, ContactMessage, SiteTraffic

@login_required
def dashboard(request):
    info = PersonalInfo.objects.first()
    experiences = Experience.objects.all().order_by('order', '-id')
    projects = Project.objects.prefetch_related('images').all().order_by('order', '-id')
    skills = Skill.objects.all()
    education = Education.objects.all()
    certifications = Certification.objects.all()
    messages = ContactMessage.objects.all().order_by('-created_at')
    traffic = SiteTraffic.objects.all().order_by('-date')

    # REDESIGNED SCORE LOGIC (100% Deterministic; NO verification needed)
    score = 0
    score_breakdown = []

    # 1. Identity & Contact Profiles (20 pts max)
    if info:
        info_pts = 0
        if info.name and info.tagline: info_pts += 5
        if info.email and info.phone: info_pts += 5
        if info.about_text and len(info.about_text) > 80: info_pts += 5
        if info.github_url or info.linkedin_url: info_pts += 5
        score += info_pts
        score_breakdown.append({'label': 'Identity & Contacts', 'points': info_pts, 'max': 20})
    else:
        score_breakdown.append({'label': 'Identity & Contacts', 'points': 0, 'max': 20})

    # 2. Work Experiences (25 pts max)
    exp_count = experiences.count()
    exp_pts = min(25, exp_count * 12) if exp_count > 0 else 0
    score += exp_pts
    score_breakdown.append({'label': 'Career Experience', 'points': exp_pts, 'max': 25})

    # 3. Project Portfolio (25 pts max)
    proj_count = projects.count()
    proj_pts = min(25, proj_count * 8) if proj_count > 0 else 0
    score += proj_pts
    score_breakdown.append({'label': 'Featured Projects', 'points': proj_pts, 'max': 25})

    # 4. Technical Skills (15 pts max)
    has_backend = skills.filter(category='backend').exists()
    has_frontend = skills.filter(category='frontend').exists()
    has_tools = skills.filter(category='tools').exists()
    skill_pts = sum([5 for condition in [has_backend, has_frontend, has_tools] if condition])
    score += skill_pts
    score_breakdown.append({'label': 'Categorized Skills', 'points': skill_pts, 'max': 15})

    # 5. Education Credentials (10 pts max)
    edu_pts = 10 if education.exists() else 0
    score += edu_pts
    score_breakdown.append({'label': 'Education Records', 'points': edu_pts, 'max': 10})

    # 6. Uploaded Certifications (5 pts max)
    cert_pts = 5 if certifications.exists() else 0
    score += cert_pts
    score_breakdown.append({'label': 'Certificates Uploaded', 'points': cert_pts, 'max': 5})

    context = {
        'info': info,
        'experiences': experiences,
        'projects': projects,
        'skills': skills,
        'education': education,
        'certifications': certifications,
        'messages': messages,
        'traffic': traffic,
        'profile_score': min(100, score),
        'score_breakdown': score_breakdown,
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


import uuid
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMessage

try:
    import llm # type: ignore
except ImportError:
    llm = None

def get_portfolio_context():
    info = PersonalInfo.objects.first()
    experiences = Experience.objects.all()
    projects = Project.objects.all()
    skills = Skill.objects.all()
    education = Education.objects.all()
    certifications = Certification.objects.all()

    context = []
    context.append("=== PRIMARY SUBJECT IDENTITY & OVERVIEW ===")
    if info:
        context.append(f"Full Name: {info.name or 'Rohan Patil'}")
        context.append(f"Title / Headline: {info.tagline or 'Full Stack & Backend Developer'}")
        context.append(f"Executive Biography: {info.about_text}")
        context.append(f"Contact Email: {info.email or 'rohanrpatil24@gmail.com'}")
        context.append(f"Contact Phone: {info.phone or '+91 9653639991'}")
        context.append(f"Location / Residence: {info.location or 'Mumbai, Maharashtra, India'}")
        context.append(f"GitHub: {info.github_url or 'Available on contact page'}")
        context.append(f"LinkedIn: {info.linkedin_url or 'Available on contact page'}")
    else:
        context.append("Candidate: Rohan Patil (Software & Backend Developer based in Mumbai, India)")

    context.append("\n=== WORK HISTORY & EXPERIENCE ===")
    if experiences.exists():
        for exp in experiences:
            context.append(f"• Role: {exp.role} at {exp.company} (Duration: {exp.duration})")
            context.append(f"  Details: {exp.description}")
    else:
        context.append("• 2+ years experience specializing in Backend APIs, Django MVT/DRF, MySQL, and Redis caching.")

    context.append("\n=== FEATURED SOFTWARE PROJECTS ===")
    if projects.exists():
        for p in projects:
            context.append(f"• Project: {p.title}")
            context.append(f"  Tech Stack: {p.tech_stack}")
            context.append(f"  Description: {p.description}")
    else:
        context.append("• Developed production REST services, WebGL portfolios, trading simulators, and responsive SPA web tools.")

    context.append("\n=== VERIFIED TECHNICAL SKILLS ===")
    if skills.exists():
        backend = [s.name for s in skills if s.category == 'backend']
        frontend = [s.name for s in skills if s.category == 'frontend']
        tools = [s.name for s in skills if s.category == 'tools']
        if backend: context.append(f"• Backend & Storage: {', '.join(backend)}")
        if frontend: context.append(f"• Frontend & Interface: {', '.join(frontend)}")
        if tools: context.append(f"• Cloud, DevOps & Tools: {', '.join(tools)}")
    else:
        context.append("• Python, Django, DRF, MySQL, Redis, JavaScript (ES6+), Three.js, React, Tailwind CSS, Git.")

    context.append("\n=== ACADEMIC BACKGROUND ===")
    if education.exists():
        for edu in education:
            context.append(f"• {edu.title} - {edu.institution} ({edu.date_completed})")

    context.append("\n=== LICENSES & CERTIFICATIONS ===")
    if certifications.exists():
        for cert in certifications:
            context.append(f"• {cert.title} issued by {cert.institution} ({cert.date_completed})")

    return "\n".join(context)

def ai_chat_page(request):
    session_id = request.session.get('ai_chat_session_id')
    if not session_id:
        room = ChatRoom.objects.create()
        request.session['ai_chat_session_id'] = str(room.session_id)
    else:
        room, _ = ChatRoom.objects.get_or_create(session_id=session_id)
    
    chat_history = room.messages.all()
    return render(request, 'core/ai_chat.html', {
        'room': room,
        'chat_history': chat_history
    })

from django.db import connection

def execute_readonly_sql(query: str):
    """
    Safely executes an arbitrary read-only query against the active database.
    Rejects any destructive or modifying keyword.
    """
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "REPLACE", "CREATE"]
    clean_q = query.strip()
    if any(word in clean_q.upper() for word in forbidden):
        return {"error": "Write and destructive operations are forbidden."}

    try:
        with connection.cursor() as cursor:
            cursor.execute(clean_q)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows[:15]]
    except Exception as e:
        return {"error": str(e)}

def get_live_database_grounding():
    """Generates a compressed, high-density factual context of the entire database."""
    info = PersonalInfo.objects.first()
    experiences = Experience.objects.all().order_by('order', '-id')
    projects = Project.objects.all().order_by('order', '-id')
    skills = Skill.objects.all()
    education = Education.objects.all()
    certifications = Certification.objects.all()

    payload = []
    if info:
        payload.append(f"CANDIDATE: {info.name} | HEADLINE: {info.tagline} | LOCATION: {info.location}")
        payload.append(f"EMAIL: {info.email} | PHONE: {info.phone} | GITHUB: {info.github_url} | LINKEDIN: {info.linkedin_url}")
        payload.append(f"BIOGRAPHY: {info.about_text}")

    if experiences.exists():
        payload.append("\nEXPERIENCE RECORDS:")
        for exp in experiences:
            payload.append(f"- {exp.role} @ {exp.company} ({exp.duration}): {exp.description}")

    if projects.exists():
        payload.append("\nPROJECT PORTFOLIO:")
        for p in projects:
            payload.append(f"- {p.title} [Stack: {p.tech_stack}]: {p.description}")

    if skills.exists():
        payload.append("\nTECHNICAL SKILLS MATRIX:")
        for s in skills:
            payload.append(f"- {s.name} ({s.category})")

    if education.exists():
        payload.append("\nEDUCATION CREDENTIALS:")
        for edu in education:
            payload.append(f"- {edu.title} from {edu.institution} ({edu.date_completed})")

    if certifications.exists():
        payload.append("\nLICENSES & CERTIFICATIONS:")
        for cert in certifications:
            payload.append(f"- {cert.title} issued by {cert.institution} ({cert.date_completed})")

    return "\n".join(payload)

def ai_chat_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        room_id = data.get('room_id')
    except Exception:
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty prompt'}, status=400)

    room = get_object_or_404(ChatRoom, session_id=room_id)
    ChatMessage.objects.create(room=room, role='user', content=user_message)

    live_context = get_live_database_grounding()

    system_prompt = f"""You are Ash, the intelligent and articulate female AI ambassador for Rohan Patil's quantum software engineering portfolio.

ACTIVE DATABASE GROUNDING:
{live_context}

RULES:
1. Ground all answers strictly on the facts, projects, roles, and contacts above.
2. If asked who you are or greeted, warmly introduce yourself as Ash.
3. If asked questions outside Rohan's background, respond:
"I am Ash, dedicated specifically to Rohan Patil's portfolio. I can only assist with questions regarding Rohan's engineering background, projects, technical skills, and experience."
4. Be concise, professional, and friendly.
"""

    bot_reply = ""
    try:
        if llm:
            model = llm.get_model("llama3.2:latest")
            recent_turns = room.messages.all().order_by('-timestamp')[:6]
            history_text = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in reversed(list(recent_turns))])
            
            prompt_str = f"{system_prompt}\n\nRecent Memory:\n{history_text}\n\nUser: {user_message}\nAsh:"
            response = model.prompt(prompt_str)
            bot_reply = response.text().strip()
        else:
            bot_reply = "Ash neural engine is standing by."
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        # Fallback keyword matching
        q = user_message.lower()
        if any(w in q for w in ['hi', 'hello', 'hey', 'who are you']):
            bot_reply = "Hello! I am Ash, Rohan Patil's AI ambassador. I can walk you through his projects, technical stack, or background. What would you like to know?"
        elif any(w in q for w in ['skill', 'stack', 'tech', 'python']):
            bot_reply = "Rohan specializes in Python, Django REST Framework, MySQL, Redis, JavaScript, React, Three.js, and PyTorch."
        elif any(w in q for w in ['project', 'work']):
            bot_reply = "Rohan has engineered scalable web architectures including this Quantum 3D Portfolio, Django REST APIs, and algorithmic trading simulators."
        elif any(w in q for w in ['contact', 'email', 'phone', 'hire']):
            bot_reply = "You can contact Rohan directly at rohanrpatil24@gmail.com or by calling +91 9653639991."
        else:
            bot_reply = "I am Ash, Rohan Patil's portfolio AI ambassador. I can only answer questions related to Rohan's engineering background, projects, technical skills, and experience. Please feel free to ask about his work!"

    ChatMessage.objects.create(room=room, role='assistant', content=bot_reply)

    return JsonResponse({'status': 'success', 'reply': bot_reply})

def download_dataset(request):
    """Allows staff/admin to download the auto-generated JSONL training dataset."""
    if not request.user.is_staff:
        raise Http404()
    count, path = generate_portfolio_dataset()
    return FileResponse(open(path, 'rb'), as_attachment=True, filename='portfolio_dataset.jsonl')


def ai_chat_reset(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    session_id = request.session.get('ai_chat_session_id')
    if session_id:
        try:
            room = ChatRoom.objects.get(session_id=session_id)
            room.messages.all().delete()
        except ChatRoom.DoesNotExist:
            pass
            
    # Generate fresh room
    new_room = ChatRoom.objects.create()
    request.session['ai_chat_session_id'] = str(new_room.session_id)

    return JsonResponse({'status': 'success', 'new_room_id': str(new_room.session_id)})

@login_required
def apps_page(request):
    return render(request, 'core/apps_page.html')