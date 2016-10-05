from django.conf.urls import url
from simple_login.views import (
    PasswordResetRequestAPIView,
    PasswordChangeAPIView,
    StatusAPIView,
    ActivationKeyRequestAPIView,
)

from chauffeur.views import (
    RegisterCustomer,
    RegisterDriver,
    ActivateAccount,
    Login,
    UserProfile,
    PushId,
    UserPublicProfile,
    ActiveRequests,
    RequestHire,
    RespondHire,
    ListRequests,
    ReviewView,
    FilterDrivers,
    GetPrice,
    PaytmView,
)
from chauffeur.models import ChauffeurUser

urlpatterns = [
    url(r'^api/user/customer-registration$', RegisterCustomer.as_view()),
    url(r'^api/user/driver-registration$', RegisterDriver.as_view()),
    url(r'^api/user/activation$', ActivateAccount.as_view()),
    url(r'^api/user/login$',  Login.as_view()),
    url(r'^api/user/forgotten-password$',
        PasswordResetRequestAPIView.as_view(user_model=ChauffeurUser)),
    url(r'^api/user/change-password$',
        PasswordChangeAPIView.as_view(user_model=ChauffeurUser)),
    url(r'^api/user/status$', StatusAPIView.as_view(user_model=ChauffeurUser)),
    url(r'^api/user/me$', UserProfile.as_view()),
    url(r'^api/user/request-activation-key$',
        ActivationKeyRequestAPIView.as_view(user_model=ChauffeurUser)),
    url(r'^api/user/push-id/add$', PushId.as_view()),
    url(r'^api/user/(?P<pk>\d+)/public-profile$', UserPublicProfile.as_view()),
    url(r'^api/user/(?P<pk>\d+)/active-requests', ActiveRequests.as_view()),
    url(r'^api/hire/create$', RequestHire.as_view()),
    url(r'^api/hire/(?P<pk>\d+)/update$', RespondHire.as_view()),
    url(r'^api/hire/list$', ListRequests.as_view()),
    url(r'^api/hire/(?P<pk>\d+)/review$', ReviewView.as_view()),
    url(r'^api/hire/filter-drivers$', FilterDrivers.as_view()),
    url(r'^api/hire/get-price$', GetPrice.as_view()),
    url(r'^api/response.cgi$', PaytmView.as_view()),
    url(r'^api/test.cgi$', PaytmView.as_view()),
]
