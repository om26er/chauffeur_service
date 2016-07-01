from django.contrib import admin
from django.contrib.auth.models import Group

from chauffeur.models import (
    ChauffeurBaseUser,
    Customer,
    Driver,
    HireRequest,
)


class PanelAdminProxy(ChauffeurBaseUser):
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        proxy = True


class DriverAdmin(admin.ModelAdmin):
    class Meta:
        model = Driver


class CustomerAdmin(admin.ModelAdmin):
    class Meta:
        model = Customer


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


class HireRequestAdmin(admin.ModelAdmin):
    class Meta:
        model = HireRequest

    def has_add_permission(self, request):
        return False


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(PanelAdminProxy, PanelAdmin)
admin.site.register(HireRequest, HireRequestAdmin)
admin.site.unregister(Group)
