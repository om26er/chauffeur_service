from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from simple_login import views as simple_login_views

from chauffeur import views as chauffeur_views
from chauffeur.models import ChauffeurBaseUser

urlpatterns = [
    url(
        r'^api/user/customer-registration$',
        chauffeur_views.RegisterCustomer.as_view()
    ),
    url(
        r'^api/user/driver-registration$',
        chauffeur_views.RegisterDriver.as_view()
    ),
    url(
        r'^api/user/activation$',
        chauffeur_views.ActivateAccount.as_view()
    ),
    url(
        r'^api/user/login$',
        chauffeur_views.Login.as_view()
    ),
    url(
        r'^api/user/forgotten-password$',
        simple_login_views.RequestPasswordReset.as_view(
            user_model=ChauffeurBaseUser
        )
    ),
    url(
        r'^api/user/change-password$',
        simple_login_views.ChangePassword.as_view(
            user_model=ChauffeurBaseUser
        )
    ),
    url(
        r'^api/user/status$',
        simple_login_views.AccountStatus.as_view(
            user_model=ChauffeurBaseUser
        )
    ),
    url(
        r'^api/user/me$',
        chauffeur_views.UserProfile.as_view()
    ),
    url(
        r'^api/user/request-activation-key$',
        simple_login_views.RequestActivationKey.as_view(
            user_model=ChauffeurBaseUser
        )
    ),
    url(
        r'^api/user/push-id/add$',
        chauffeur_views.ListRequests.as_view()
    ),
    url(
        r'^api/user/(?P<pk>\d+)/public-profile$',
        chauffeur_views.ListRequests.as_view()
    ),
    url(
        r'^api/hire/create$',
        chauffeur_views.RequestHire.as_view()
    ),
    url(
        r'^api/hire/(?P<pk>\d+)/update$',
        chauffeur_views.RespondHire.as_view()
    ),
    url(
        r'^api/hire/list$',
        chauffeur_views.ListRequests.as_view()
    ),
    url(
        r'^api/hire/(?P<pk>\d+)/review$',
        chauffeur_views.ReviewView.as_view()
    ),
    url(
        r'^api/hire/filter-drivers$',
        chauffeur_views.FilterDrivers.as_view()
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
