from django.contrib import admin
from django.contrib.auth.models import Group

from chauffeur.models import (
    User,
    HireRequest,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER
)


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

    fields = (
        'is_active',
        'status',
        'email',
        'password',
        'full_name',
        'phone_number',
        'transmission_type',
        'photo',
        'location',
        'location_last_updated',
        'driving_experience',
        'number_of_hires',
        'bio',
        'review_count',
        'review_stars',
        'location_reporting_type',
        'location_reporting_interval',
    )

    class Meta:
        model = DriverProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_DRIVER)

    def has_add_permission(self, request):
        return False


class CustomerAdmin(admin.ModelAdmin):
    fields = (
        'is_active',
        'email',
        'password',
        'full_name',
        'phone_number',
        'transmission_type',
        'photo',
        'location',
        'number_of_hires',
        'vehicle_type',
        'vehicle_make',
        'vehicle_model',
        'initial_app_payment',
        'review_count',
        'review_stars',
        'driver_filter_radius',
    )

    class Meta:
        model = CustomerProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_CUSTOMER)

    def has_add_permission(self, request):
        return False


class PanelAdmin(admin.ModelAdmin):
    fields = (
        'password',
        'full_name',
        'email',
        'is_active',
        'is_superuser',
        'last_login',
        'groups',
        'user_permissions',
    )

    class Meta:
        model = PanelAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(is_admin=True)


class HireRequestAdmin(admin.ModelAdmin):
    class Meta:
        model = HireRequest


admin.site.register(CustomerProxy, CustomerAdmin)
admin.site.register(DriverProxy, DriverAdmin)
admin.site.register(PanelAdminProxy, PanelAdmin)
admin.site.register(HireRequest, HireRequestAdmin)
admin.site.unregister(Group)
