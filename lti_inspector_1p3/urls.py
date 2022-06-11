from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('', include('inspector.urls')),
    path('lti_inspector_admin/', admin.site.urls),
]
