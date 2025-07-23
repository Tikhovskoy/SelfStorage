from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name', 'phone', 'registered_at']
	readonly_fields = ['registered_at']
