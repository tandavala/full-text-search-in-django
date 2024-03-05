from django.conf import settings
from django.contrib import admin
from django.urls import path, include

import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/catalog/', include('catalog.urls'))
]

if settings.DEBUG or settings.TESTING_MODE:  # changed
    urlpatterns = [
        path('debug/', include(debug_toolbar.urls)),
    ] + urlpatterns
