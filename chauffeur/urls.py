from django.conf.urls import url

from chauffeur import views

urlpatterns = [
    url(r'^api/register_customer$', views.CustomerRegistrationView.as_view()),
    url(r'^api/register_driver$', views.DriverRegistrationView.as_view()),

    url(r'^api/customers$', views.CustomersListView.as_view()),
    url(r'^api/drivers$', views.DriversListView.as_view()),

    url(r'^api/customers/(?P<pk>[0-9]+)$', views.CustomerView.as_view()),
    url(r'^api/drivers/(?P<pk>[0-9]+)$', views.DriverView.as_view()),
]
