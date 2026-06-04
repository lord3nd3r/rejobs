from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from apps.jobs.sitemaps import JobListingSitemap, JobCategorySitemap, StaticViewSitemap

sitemaps = {
    'jobs': JobListingSitemap,
    'categories': JobCategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.jobs.urls', namespace='jobs')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('apply/', include('apps.applications.urls', namespace='applications')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('dashboard/', include('apps.accounts.dashboard_urls', namespace='dashboard')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
