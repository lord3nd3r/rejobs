from django.contrib import admin
from .models import JobCategory, JobListing


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'job_type', 'status', 'is_featured', 'posted_at')
    list_filter = ('status', 'job_type', 'work_mode', 'is_featured', 'category')
    search_fields = ('title', 'employer__company_name')
    raw_id_fields = ('employer',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_at'
    readonly_fields = ('posted_at', 'created_at', 'updated_at')

    actions = ['mark_active', 'mark_closed']

    @admin.action(description='Mark selected listings as Active')
    def mark_active(self, request, queryset):
        queryset.update(status=JobListing.ACTIVE)

    @admin.action(description='Mark selected listings as Closed')
    def mark_closed(self, request, queryset):
        queryset.update(status=JobListing.CLOSED)
