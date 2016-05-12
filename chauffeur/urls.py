from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken import views

from chauffeur import views as chauffeur_views

urlpatterns = [
    url(r'^api/accounts/login$', views.obtain_auth_token),
    url(r'^api/accounts/activate$',
        chauffeur_views.AccountActivationView.as_view()),
    url(r'^api/accounts/reset_password$',
        chauffeur_views.RequestPasswordResetView.as_view()),
    url(r'^api/accounts/change_password$',
        chauffeur_views.PasswordChangeView.as_view()),
    url(r'^api/accounts/status$', chauffeur_views.UserStatusView.as_view()),
    url(r'^api/accounts/me$', chauffeur_views.UserDetailsView.as_view()),
    url(r'^api/accounts/request_activation_key$',
        chauffeur_views.ActivationKeyView.as_view()),

    url(r'^api/register_customer$',
        chauffeur_views.CustomerRegistrationView.as_view()),
    url(r'^api/register_driver$',
        chauffeur_views.DriverRegistrationView.as_view()),

    url(r'^api/customers/(?P<pk>[0-9]+)$',
        chauffeur_views.CustomerView.as_view()),
    url(r'^api/drivers/(?P<pk>[0-9]+)$',
        chauffeur_views.DriverView.as_view()),

    url(r'^api/drivers_around$', chauffeur_views.DriversAroundView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
