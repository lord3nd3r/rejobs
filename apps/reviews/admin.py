from django.contrib import admin
from .models import ReviewAssignment, ReviewNote


class ReviewNoteInline(admin.TabularInline):
    model = ReviewNote
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    list_display = ('application', 'reviewer', 'status', 'assigned_at', 'due_date', 'completed_at')
    list_filter = ('status',)
    search_fields = ('application__applicant__email', 'reviewer__email')
    raw_id_fields = ('application', 'reviewer')
    readonly_fields = ('assigned_at', 'completed_at')
    inlines = [ReviewNoteInline]


@admin.register(ReviewNote)
class ReviewNoteAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'recommendation', 'is_final', 'created_at')
    list_filter = ('recommendation', 'is_final')
    readonly_fields = ('created_at',)
