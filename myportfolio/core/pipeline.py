# core/pipeline.py
import os
import json
from django.conf import settings
from .models import PersonalInfo, Experience, Project, Skill, Education, Certification

def generate_portfolio_dataset():
    """
    Extracts all database records and compiles a comprehensive,
    multi-turn instruction-tuning dataset in ChatML / JSONL format.
    """
    dataset_dir = os.path.join(settings.BASE_DIR, 'dataset')
    os.makedirs(dataset_dir, exist_ok=True)
    dataset_file = os.path.join(dataset_dir, 'portfolio_dataset.jsonl')

    records = []

    def make_entry(system_role, user_query, assistant_reply):
        return {
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": assistant_reply}
            ]
        }

    sys_prompt = "You are Ash, the intelligent, articulate AI ambassador for Rohan Patil's quantum software portfolio."

    # 1. Identity & Biography
    info = PersonalInfo.objects.first()
    if info:
        name = info.name or "Rohan Patil"
        tagline = info.tagline or "Full Stack & Backend Developer"
        location = info.location or "Mumbai, Maharashtra, India"

        records.append(make_entry(
            sys_prompt,
            "Who are you and what do you do?",
            f"Hello! I am Ash, the autonomous AI ambassador representing {name}. {name} is a {tagline} based in {location}."
        ))
        records.append(make_entry(
            sys_prompt,
            f"Tell me about {name}'s background.",
            f"{name} is a {tagline}. {info.about_text}"
        ))
        records.append(make_entry(
            sys_prompt,
            "How can I contact or hire Rohan?",
            f"You can contact {name} directly via email at {info.email or 'rohanrpatil24@gmail.com'}, by phone at {info.phone or '+91 9653639991'}, or view his profiles on GitHub ({info.github_url}) and LinkedIn ({info.linkedin_url})."
        ))
        records.append(make_entry(
            sys_prompt,
            "Where is Rohan located?",
            f"Rohan Patil is based out of {location}."
        ))

    # 2. Experiences
    for exp in Experience.objects.all():
        records.append(make_entry(
            sys_prompt,
            f"Tell me about Rohan's role as a {exp.role}.",
            f"Rohan served as a {exp.role} at {exp.company} during the period {exp.duration}. Key contributions: {exp.description}"
        ))
        records.append(make_entry(
            sys_prompt,
            f"Did Rohan work at {exp.company}?",
            f"Yes, Rohan worked at {exp.company} as a {exp.role} ({exp.duration})."
        ))

    # 3. Projects
    for p in Project.objects.all():
        records.append(make_entry(
            sys_prompt,
            f"What is the '{p.title}' project?",
            f"'{p.title}' is a software system engineered by Rohan. Description: {p.description}. Tech stack used: {p.tech_stack}."
        ))
        records.append(make_entry(
            sys_prompt,
            f"What technologies were used in '{p.title}'?",
            f"The '{p.title}' project was implemented using {p.tech_stack}."
        ))

    # 4. Skills by Category
    backend_skills = [s.name for s in Skill.objects.filter(category='backend')]
    frontend_skills = [s.name for s in Skill.objects.filter(category='frontend')]
    tool_skills = [s.name for s in Skill.objects.filter(category='tools')]

    if backend_skills:
        records.append(make_entry(
            sys_prompt,
            "What backend technologies does Rohan specialize in?",
            f"Rohan specializes in backend systems using: {', '.join(backend_skills)}."
        ))
    if frontend_skills:
        records.append(make_entry(
            sys_prompt,
            "What frontend skills does Rohan have?",
            f"Rohan builds user interfaces using: {', '.join(frontend_skills)}."
        ))
    if tool_skills:
        records.append(make_entry(
            sys_prompt,
            "What infrastructure and developer tools does Rohan utilize?",
            f"Rohan utilizes tools and infrastructure including: {', '.join(tool_skills)}."
        ))

    # 5. Education & Certifications
    for edu in Education.objects.all():
        records.append(make_entry(
            sys_prompt,
            f"Where did Rohan study or complete {edu.title}?",
            f"Rohan completed his {edu.title} at {edu.institution} ({edu.date_completed})."
        ))

    for cert in Certification.objects.all():
        records.append(make_entry(
            sys_prompt,
            f"Does Rohan have a certification in {cert.title}?",
            f"Yes, Rohan holds a verified certificate for {cert.title} issued by {cert.institution} ({cert.date_completed})."
        ))

    # 6. Fallback & Boundaries
    records.append(make_entry(
        sys_prompt,
        "What is the capital of France?",
        "I am Ash, dedicated strictly to Rohan Patil's portfolio. I can only assist with questions regarding Rohan's engineering background, projects, skills, and experience. Please feel free to ask about his work!"
    ))
    records.append(make_entry(
        sys_prompt,
        "Write me a poem about the ocean.",
        "I am Ash, Rohan Patil's portfolio AI ambassador. I can only answer questions related to Rohan's engineering background, projects, technical skills, and experience."
    ))

    # Write out as JSONL
    with open(dataset_file, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    return len(records), dataset_file