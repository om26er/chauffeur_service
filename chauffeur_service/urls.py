from django.conf.urls import include, url
from django.contrib import admin

from chauffeur import urls as chauffeur_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(chauffeur_urls))
]
