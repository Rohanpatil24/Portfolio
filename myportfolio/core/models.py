import os
from django.db import models
from django.utils import timezone

class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=255)
    about_text = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    location = models.CharField(max_length=100)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.name

class Experience(models.Model):
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.role} - {self.company}"

class Project(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, default='ph-fill ph-folder')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend & Databases'),
        ('frontend', 'Frontend'),
        ('tools', 'Cloud & Tools'),
    ]
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Education(models.Model):
    title = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    date_completed = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Certification(models.Model):
    title = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    date_completed = models.CharField(max_length=50)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

    @property
    def is_pdf(self):
        if self.file and self.file.name:
            return self.file.name.lower().endswith('.pdf')
        return False

    def __str__(self):
        return self.title

class SiteTraffic(models.Model):
    date = models.DateField(auto_now_add=True, unique=True)
    hits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.hits} hits"

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

import uuid

class ChatRoom(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.session_id}"

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.role}] {self.room.session_id}: {self.content[:40]}"