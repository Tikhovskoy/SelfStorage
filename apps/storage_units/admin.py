from django.contrib import admin
from .models import Warehouse, Box


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
	list_display = ['name', 'address', 'temperature']
	search_fields = ['name', 'address']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
	list_display = ['warehouse', 'floor', 'square', 'height', 'price', 'is_free']
	list_filter = ['warehouse', 'square', 'height', 'is_free']
