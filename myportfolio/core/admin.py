from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PersonalInfo,
    Experience,
    Project,
    ProjectImage,
    Skill,
    Education,
    Certification,
)


def get_model_fields(model, exclude=None):
    """Safely extracts real concrete field names from a model."""
    exclude = exclude or ['id']
    return [
        field.name
        for field in model._meta.fields
        if field.name not in exclude and not field.is_relation
    ]


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    max_num = 10
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        # Look for typical image field names
        img = getattr(obj, 'image', None) or getattr(obj, 'file', None)
        if img and hasattr(img, 'url'):
            return format_html(
                '<img src="{}" style="height: 50px; width: auto; border-radius: 4px;" />',
                img.url,
            )
        return "-"
    image_preview.short_description = "Preview"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Uses existing Project fields: title, role, order
    list_display = [f for f in ['title', 'role', 'order'] if hasattr(Project, f)]
    list_filter = [f for f in ['role'] if hasattr(Project, f)]
    search_fields = [f for f in ['title', 'tech_stack', 'description'] if hasattr(Project, f)]
    inlines = [ProjectImageInline]

    if 'order' in [f.name for f in Project._meta.fields]:
        list_editable = ('order',)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    readonly_fields = ('image_preview',)

    def get_list_display(self, request):
        fields = [f.name for f in self.model._meta.fields if f.name != 'id']
        return fields + ['image_preview']

    def image_preview(self, obj):
        img = getattr(obj, 'image', None) or getattr(obj, 'file', None)
        if img and hasattr(img, 'url'):
            return format_html(
                '<img src="{}" style="height: 60px; width: auto; border-radius: 4px;" />',
                img.url,
            )
        return "-"
    image_preview.short_description = "Preview"


@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return get_model_fields(self.model)[:5]

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return get_model_fields(self.model)[:6]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return get_model_fields(self.model)[:5]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return get_model_fields(self.model)[:6]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return get_model_fields(self.model)[:5]