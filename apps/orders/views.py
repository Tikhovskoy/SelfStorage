from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from apps.orders.forms import LoginForm, RegistrationForm


def _safe_redirect(request, *candidates):
    """Перенаправляет на первый безопасный адрес из кандидатов, иначе на главную.

    Безопасный — это адрес нашего же сайта: next из формы и Referer приходят от
    клиента, и без проверки их можно использовать для отправки на чужой сайт.
    """
    for url in candidates:
        if url and url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(url)
    return redirect("/")


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return _safe_redirect(
                request, request.POST.get("next"), request.META.get("HTTP_REFERER")
            )
        else:
            messages.error(request, "Ошибка регистрации")

    return _safe_redirect(request, request.META.get("HTTP_REFERER"))


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return _safe_redirect(
                request, request.POST.get("next"), request.META.get("HTTP_REFERER")
            )
        else:
            messages.error(request, "Неверный логин или пароль")

    return _safe_redirect(request, request.META.get("HTTP_REFERER"))


def logout_view(request):
    referer = request.META.get("HTTP_REFERER", "/")
    if "/my-rent" in referer:
        referer = "/"
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта.")
    return _safe_redirect(request, referer)
