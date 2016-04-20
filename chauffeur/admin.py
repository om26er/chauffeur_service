from django.contrib import admin
from django.contrib.auth.models import Group

from chauffeur.models import User, USER_TYPE_CUSTOMER, USER_TYPE_DRIVER


class CustomerProxy(User):
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        proxy = True


class DriverProxy(User):
    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        proxy = True


class PanelAdminProxy(User):
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        proxy = True


class DriverAdmin(admin.ModelAdmin):

    fields = ('is_active', 'username', 'password', 'first_name', 'last_name',
              'email', 'phone_number', 'photo', 'location',
              'location_last_updated', 'driving_experience', 'number_of_hires',
              'bio')

    class Meta:
        model = DriverProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_DRIVER)


class CustomerAdmin(admin.ModelAdmin):
    fields = ('is_active', 'username', 'password', 'first_name', 'last_name',
              'email', 'phone_number', 'photo', 'location', 'number_of_hires',
              'vehicle_type', 'vehicle_category', 'vehicle_make',
              'vehicle_model', 'initial_app_payment')

    class Meta:
        model = CustomerProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_CUSTOMER)


class PanelAdmin(admin.ModelAdmin):
    fields = ('username', 'password', 'first_name', 'last_name', 'email',
              'is_active', 'is_superuser', 'is_staff', 'last_login',
              'date_joined', 'groups', 'user_permissions')

    class Meta:
        model = PanelAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(is_staff=True)


admin.site.register(CustomerProxy, CustomerAdmin)
admin.site.register(DriverProxy, DriverAdmin)
admin.site.register(PanelAdminProxy, PanelAdmin)
admin.site.unregister(Group)
