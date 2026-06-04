from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.jobs.models import JobListing, JobCategory


class JobListingSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return JobListing.objects.filter(status=JobListing.ACTIVE).select_related('employer')

    def location(self, obj):
        return reverse('jobs:detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


class JobCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return JobCategory.objects.all()

    def location(self, obj):
        return f"{reverse('jobs:list')}?category={obj.slug}"


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return ['jobs:list', 'billing:plans', 'accounts:register']

    def location(self, item):
        return reverse(item)
