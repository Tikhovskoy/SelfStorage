from django.urls import path
from .views import index, boxes_list, faq, my_rent, my_rent_empty, boxes, tariffs_view, calculate_cost_view

app_name = 'storage_units'

urlpatterns = [
    path('', index, name='index'),
    path('boxes/', boxes_list, name='boxes'),
    path('faq/', faq, name='faq'),
    path('my-rent/', my_rent, name='my_rent'),
    path('my-rent-empty/', my_rent_empty, name='my_rent_empty'),
    path('boxes/', boxes, name='boxes'),
    path('tariffs/', tariffs_view, name='tariffs'),
    path('calculate-cost/', calculate_cost_view, name='calculate_cost'),
]
