from django.contrib import admin

from .models import DonationSettings


@admin.register(DonationSettings)
class DonationSettingsAdmin(admin.ModelAdmin):
    fields = ("paypal_url", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not DonationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

