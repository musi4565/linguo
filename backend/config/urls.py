from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.users.views import ChangePasswordView, ProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/profile/", ProfileView.as_view()),
    path("api/profile/password/", ChangePasswordView.as_view()),
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.progress.urls")),
    path("api/", include("apps.bookmarks.urls")),
    path("api/", include("apps.achievements.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
