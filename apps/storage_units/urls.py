from django.urls import path

from apps.orders.views import (
    login_view,
    logout_view,
    register_view,
    simple_password_reset_view,
)

from .views import (
    PrivacyPolicyView,
    boxes_list_view,
    calculate_cost_view,
    cost_confirmation,
    faq,
    handle_email_cost_request,
    index,
    my_rent,
    my_rent_empty,
    renew_box,
    rent_box,
    tariffs_view,
)

app_name = "storage_units"

urlpatterns = [
    path("", index, name="index"),
    path("boxes/", boxes_list_view, name="boxes_list"),
    path("faq/", faq, name="faq"),
    path("my-rent/", my_rent, name="my_rent"),
    path("my-rent-empty/", my_rent_empty, name="my_rent_empty"),
    path("tariffs/", tariffs_view, name="tariffs"),
    path("calculate-cost/", calculate_cost_view, name="calculate_cost"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("simple-reset/", simple_password_reset_view, name="simple_password_reset"),
    path("my-rent/<int:box_id>/renew/", renew_box, name="renew_box"),
    path("rent/<int:box_id>/", rent_box, name="rent_box"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("cost-confirmation/", cost_confirmation, name="cost_confirmation"),
    path("submit-cost-request/", handle_email_cost_request, name="submit_cost_request"),
]
