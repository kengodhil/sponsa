from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from apps.sponsors.views import home

admin.site.site_header = "Sponsa control room"
admin.site.site_title = "Sponsa admin"
admin.site.index_title = "Users, numbers and sponsor profiles"

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", home, name="home"),
    path("", include("apps.accounts.urls")),
    path("", include("apps.sponsors.urls")),
    path("pay/", include("apps.payments.urls")),
    path("inbox/", include("apps.messaging.urls")),
    path("control/", include("apps.staff.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
