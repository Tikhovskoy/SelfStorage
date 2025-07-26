from django.urls import path
from .views import index, boxes_list, faq, my_rent, my_rent_empty, tariffs_view, calculate_cost_view, boxes_list_view
from apps.orders.views import register_view, login_view, logout_view, simple_password_reset_view

app_name = 'storage_units'

urlpatterns = [
    path('', index, name='index'),
    path('boxes/', boxes_list_view, name='boxes_list'),
    path('faq/', faq, name='faq'),
    path('my-rent/', my_rent, name='my_rent'),
    path('my-rent-empty/', my_rent_empty, name='my_rent_empty'),
    path('tariffs/', tariffs_view, name='tariffs'),
    path('calculate-cost/', calculate_cost_view, name='calculate_cost'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('simple-reset/', simple_password_reset_view, name='simple_password_reset'),
]
