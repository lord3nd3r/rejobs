from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.jobs.urls', namespace='jobs')),           # / → job list (homepage)
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('apply/', include('apps.applications.urls', namespace='applications')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('dashboard/', include('apps.accounts.dashboard_urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
