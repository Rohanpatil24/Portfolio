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


import json
import json
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import (
    PersonalInfo, Experience, Project, Skill,
    Education, Certification, ChatRoom, ChatMessage
)

try:
    import llm
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

import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.db import connection
from .models import (
    PersonalInfo, Experience, Project, Skill,
    Education, Certification, ChatRoom, ChatMessage
)
from .pipeline import generate_portfolio_dataset

logger = logging.getLogger(__name__)

try:
    import llm
except ImportError:
    llm = None

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
            model = llm.get_model()
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
            model = llm.get_model()
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