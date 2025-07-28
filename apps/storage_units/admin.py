from django.contrib import admin
from .models import Warehouse, Box, Tariff, Rental


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'temperature']
    search_fields = ['name', 'address']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['id', 'warehouse', 'floor', 'square', 'height', 'price', 'is_free']
    list_filter = ['warehouse', 'square', 'height', 'is_free']
    search_fields = ['id', 'tenant__user__email']
    readonly_fields = ['square']


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'min_square_meters', 'max_square_meters']
    list_filter = ['min_square_meters']
    search_fields = ['name']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('client', 'box', 'start_date', 'end_date')