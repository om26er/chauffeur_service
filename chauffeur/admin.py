from django.contrib import admin
from django.contrib.auth.models import Group

from chauffeur.models import (
    ChauffeurUser,
    Charge,
    HireRequest,
    PricingPdf,
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


class DriversPendingApprovalAdminProxy(ChauffeurUser):
    class Meta:
        verbose_name = 'Pending Driver'
        verbose_name_plural = 'Pending Drivers'
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
    fields = (
        'user_type',
        'password',
        'email',
        'full_name',
        'phone_number',
        'photo',
        'number_of_hires',
        'review_count',
        'review_stars',
        'transmission_type',
        'vehicle_type',
        'vehicle_make',
        'vehicle_model',
        'vehicle_model_year',
        'initial_app_payment',
        'driver_filter_radius',
    )
    readonly_fields = (
        'email',
        'password',
    )

    class Meta:
        model = CustomerAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(user_type=USER_TYPE_CUSTOMER)


class DriverAdmin(admin.ModelAdmin):
    fields = (
        'is_approved_by_admin',
        'user_type',
        'password',
        'email',
        'gender',
        'full_name',
        'phone_number',
        'photo',
        'number_of_hires',
        'review_count',
        'review_stars',
        'transmission_type',
        'location',
        'location_last_updated',
        'driving_experience',
        'bio',
        'status',
        'location_reporting_type',
        'location_reporting_interval',
        'doc1',
        'doc2',
        'doc3',
    )
    readonly_fields = (
        'email',
        'password',
    )

    class Meta:
        model = DriverAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(
            user_type=USER_TYPE_DRIVER,
            is_approved_by_admin=True
        )


class DriversPendingApprovalAdmin(admin.ModelAdmin):
    fields = (
        'is_approved_by_admin',
        'user_type',
        'password',
        'email',
        'gender',
        'full_name',
        'phone_number',
        'photo',
        'number_of_hires',
        'review_count',
        'review_stars',
        'transmission_type',
        'location',
        'location_last_updated',
        'driving_experience',
        'bio',
        'status',
        'location_reporting_type',
        'location_reporting_interval',
        'doc1',
        'doc2',
        'doc3',
    )
    readonly_fields = (
        'email',
        'password',
    )

    class Meta:
        model = DriverAdminProxy

    def get_queryset(self, request):
        return self.model.objects.filter(
            user_type=USER_TYPE_DRIVER,
            is_approved_by_admin=False
        )


class HireRequestAdmin(admin.ModelAdmin):
    class Meta:
        model = HireRequest

    def has_add_permission(self, request):
        return False


class PricingPdfAdmin(admin.ModelAdmin):
    class Meta:
        model = PricingPdf


class ChargeAdmin(admin.ModelAdmin):
    class Meta:
        model = Charge


class SegmentAdmin(admin.ModelAdmin):
    class Meta:
        model = Segment


admin.site.register(CustomerAdminProxy, CustomerAdmin)
admin.site.register(DriverAdminProxy, DriverAdmin)
admin.site.register(
    DriversPendingApprovalAdminProxy,
    DriversPendingApprovalAdmin
)
admin.site.register(PanelAdminProxy, PanelAdmin)
admin.site.register(HireRequest, HireRequestAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(PricingPdf, PricingPdfAdmin)
admin.site.unregister(Group)
