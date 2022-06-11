from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from .views import login, launch, get_jwks, config

urlpatterns = [
    url(r'^login/$', login, name='inspector-login'),
    url(r'^launch/$', launch, name='inspector-launch'),
    url(r'^jwks/$', get_jwks, name='inspector-jwks'),
    url(r'^config/$', config, name='inspector-config'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
