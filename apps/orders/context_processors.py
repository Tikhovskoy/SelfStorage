from django.contrib.auth.forms import AuthenticationForm

from apps.orders.forms import RegistrationForm


def auth_forms(request):
    return {
        "login_form": AuthenticationForm(),
        "registration_form": RegistrationForm(),
    }
