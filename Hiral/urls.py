
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('Recruiter.urls')),
    path('Recruiter/', include('Recruiter.urls')),
    path('accounts/', include('accounts.urls')),
    path('Seeker/', include('Seeker.urls')),
    path("chat/", include("chat.urls")),
    path("api/chat/", include("chat.api.urls")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)