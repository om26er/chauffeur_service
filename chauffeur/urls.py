from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from simple_login import views as simple_login_views

from chauffeur import views as chauffeur_views
from chauffeur.models import User

urlpatterns = [
    url(
        r'^api/accounts/login$',
        simple_login_views.Login.as_view(user_model=User)
    ),
    url(
        r'^api/accounts/activate$',
        chauffeur_views.ActivateAccount.as_view(user_model=User)
    ),
    url(
        r'^api/accounts/reset_password$',
        simple_login_views.RequestPasswordReset.as_view(user_model=User)
    ),
    url(
        r'^api/accounts/change_password$',
        simple_login_views.ChangePassword.as_view(user_model=User)
    ),
    url(
        r'^api/accounts/status$',
        simple_login_views.AccountStatus.as_view(user_model=User)
    ),
    url(
        r'^api/accounts/me$',
        chauffeur_views.UserProfile.as_view()
    ),
    url(
        r'^api/accounts/request_activation_key$',
        simple_login_views.RequestActivationKey.as_view(user_model=User)
    ),
    url(
        r'^api/register_customer$',
        chauffeur_views.RegisterCustomer.as_view()
    ),
    url(
        r'^api/register_driver$',
        chauffeur_views.RegisterDriver.as_view()
    ),
    url(
        r'^api/hire$',
        chauffeur_views.RequestHire.as_view()
    ),
    url(
        r'^api/hire_response$',
        chauffeur_views.RespondHire.as_view()
    ),
    url(
        r'^api/filter_drivers$',
        chauffeur_views.FilterDrivers.as_view()
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
