from django.contrib import admin

from .models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "active_from",
        "active_to",
        "usage_limit",
        "used_count",
        "one_time_per_user",
        "used_clients_count",
    )
    search_fields = ("code",)
    list_filter = ("active_from", "active_to", "one_time_per_user")
    filter_horizontal = ("used_clients",)

    @admin.display(description="Клиентов использовало")
    def used_clients_count(self, obj):
        return obj.used_clients.count()
