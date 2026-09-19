from django.db import models

class PersonalInfo(models.Model):
    name = models.CharField(max_length=100, default="Rohan Patil")
    tagline = models.CharField(max_length=200)
    about_text = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Experience(models.Model):
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    duration = models.CharField(max_length=50, help_text="e.g., Oct 2024 - Present")
    description = models.TextField(help_text="Separate bullet points with a new line")
    order = models.IntegerField(default=0, help_text="Order to display on page (lower is first)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.role} at {self.company}"

class Project(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200, help_text="Comma-separated (e.g., Django, MySQL, Redis)")
    github_link = models.URLField(blank=True)
    icon_class = models.CharField(max_length=50, default="ph-folder")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('backend', 'Backend & Databases'),
        ('frontend', 'Frontend'),
        ('tools', 'Cloud & Tools'),
    )
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Education(models.Model):
    title = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    date_completed = models.CharField(max_length=50)
    is_certification = models.BooleanField(default=False)

    def __str__(self):
        return self.title