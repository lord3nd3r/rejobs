from django.contrib import admin
from .models import Application, WorkExperience, Education, Skill


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('applicant__email', 'job__title')
    raw_id_fields = ('applicant', 'job')
    readonly_fields = ('applied_at', 'updated_at')
    inlines = [WorkExperienceInline, EducationInline, SkillInline]

    actions = ['mark_under_review', 'mark_shortlisted', 'mark_rejected']

    @admin.action(description='Mark selected as Under Review')
    def mark_under_review(self, request, queryset):
        queryset.update(status=Application.UNDER_REVIEW)

    @admin.action(description='Mark selected as Shortlisted')
    def mark_shortlisted(self, request, queryset):
        queryset.update(status=Application.SHORTLISTED)

    @admin.action(description='Mark selected as Rejected')
    def mark_rejected(self, request, queryset):
        queryset.update(status=Application.REJECTED)
