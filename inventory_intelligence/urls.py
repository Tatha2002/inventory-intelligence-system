from django.urls import path, include
from django.contrib import admin
from accounts.views import home
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('', home, name='home'),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('manager/', include('manager_portal.urls')),
    path('staff/', include('staff_portal.urls')),
    path("machine-learning/", include("machine_learning.urls")),
    path("nlp/", include("nlp.urls")),
    path('api/', include('api.urls')),
    path("staff/ann/", include("ann_prediction.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
