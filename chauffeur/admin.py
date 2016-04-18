from django.contrib import admin

from chauffeur.models import Driver, Customer


class DriverAdmin(admin.ModelAdmin):
    pass


class CustomerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Driver, DriverAdmin)
admin.site.register(Customer, CustomerAdmin)
