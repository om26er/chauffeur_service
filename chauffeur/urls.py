from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken import views

from chauffeur import views as chauffeur_views

urlpatterns = [
    url(r'^api/login$', views.obtain_auth_token),
    url(r'^api/activate$', chauffeur_views.AccountActivationView.as_view()),
    url(r'^api/reset', chauffeur_views.RequestPasswordResetView.as_view()),
    url(r'^api/change_password',
        chauffeur_views.PasswordChangeWithKeyView.as_view()),

    url(r'^api/register_customer$',
        chauffeur_views.CustomerRegistrationView.as_view()),
    url(r'^api/register_driver$',
        chauffeur_views.DriverRegistrationView.as_view()),

    url(r'^api/customers/(?P<pk>[0-9]+)$',
        chauffeur_views.CustomerView.as_view()),
    url(r'^api/drivers/(?P<pk>[0-9]+)$',
        chauffeur_views.DriverView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
