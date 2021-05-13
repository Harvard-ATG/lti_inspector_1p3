from django.urls import path
from .views import launch, login, get_jwks

urlpatterns = [
    path('login/', login, name='inspector-login'),
    path('launch/', launch, name='inspector-launch'),
    path('jwks/', get_jwks, name='inspector-jwks'),
]
