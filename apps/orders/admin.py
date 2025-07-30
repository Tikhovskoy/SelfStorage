from django.contrib import admin

from .models import Client, CostCalculationRequest


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone", "registered_at"]
    readonly_fields = ["registered_at"]


@admin.register(CostCalculationRequest)
class CostCalculationRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "is_processed")
    list_filter = ("is_processed",)
    search_fields = ("email",)
    list_editable = ("is_processed",)
