from django.conf import settings
from django.utils.html import format_html
from django.contrib import admin
from .models import ShortLink
from django.contrib.admin import display

@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("token", "target_url", "click_count", "created_at", "short_url_display")
    readonly_fields = ("click_count", "short_url_display")

    @display(description="Короткая ссылка")
    def short_url_display(self, obj):
        domain = settings.SELFSTORAGE_DOMAIN
        url = f"http://{domain}/s/{obj.token}/"
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)
