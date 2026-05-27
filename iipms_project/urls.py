# =============================================================
# urls.py  (iipms_project — the project root)
# This is the TOP-LEVEL URL file.
# It includes the app's URLs and also sets up the admin panel
# and media file serving during development.
# =============================================================

from django.contrib import admin
from django.urls     import path, include
from django.conf     import settings
from django.conf.urls.static import static

urlpatterns = [

    # Django's built-in admin panel — visit /admin/ in the browser
    path("admin/", admin.site.urls),

    # All of our app's URLs (defined in iipms_app/urls.py)
    path("", include("iipms_app.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ↑ This last line makes Django serve uploaded photos and CVs during development.
#   In production, your web server (nginx/Apache) handles this instead.
