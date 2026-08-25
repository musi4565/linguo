from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve

from apps.users.views import ChangePasswordView, ProfileView


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/profile/", ProfileView.as_view()),
    path("api/profile/password/", ChangePasswordView.as_view()),
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.progress.urls")),
    path("api/", include("apps.bookmarks.urls")),
    path("api/", include("apps.achievements.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
