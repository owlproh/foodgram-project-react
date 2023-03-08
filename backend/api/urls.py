from django.urls import include, path

from .v1 import urls

app_name = 'api'

urlpatterns = [
    path('', include(urls)),
]
