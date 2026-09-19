from django.contrib import admin
from .models import PersonalInfo, Experience, Project, Skill, Education

admin.site.register(PersonalInfo)
admin.site.register(Experience)
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Education)