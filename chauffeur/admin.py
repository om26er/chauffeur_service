from django.contrib import admin
from django.contrib.auth.models import Group

from chauffeur.models import (
    ChauffeurUser,
    Charge,
    HireRequest,
    Segment,
    USER_TYPE_CUSTOMER,
    USER_TYPE_DRIVER,
)


class PanelAdminProxy(ChauffeurUser):
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        proxy = True


class CustomerAdminProxy(ChauffeurUser):
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        proxy = True


class DriverAdminProxy(ChauffeurUser):
    class Meta:
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        proxy = True


class PanelAdmin(admin.ModelAdmin):
    fields = (
        'email',
        'password',
        'full_name',
        'is_active',
        'is_superuser',
        'last_login',
        'groups',
        'user_permissions',
    )
    readonly_fields = (
        'email',
        'password',
    )

    class Meta:
        model = PanelAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(is_admin=True)


class CustomerAdmin(admin.ModelAdmin):
    class Meta:
        model = CustomerAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_CUSTOMER)


class DriverAdmin(admin.ModelAdmin):
    class Meta:
        model = DriverAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_DRIVER)


class HireRequestAdmin(admin.ModelAdmin):
    class Meta:
        model = HireRequest

    def has_add_permission(self, request):
        return False


class ChargeAdmin(admin.ModelAdmin):
    class Meta:
        model = Charge


class SegmentAdmin(admin.ModelAdmin):
    class Meta:
        model = Segment


admin.site.register(CustomerAdminProxy, CustomerAdmin)
admin.site.register(DriverAdminProxy, DriverAdmin)
admin.site.register(PanelAdminProxy, PanelAdmin)
admin.site.register(HireRequest, HireRequestAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.unregister(Group)
