from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib import messages

from apps.orders.forms import RegistrationForm, LoginForm
from .forms import SimplePasswordResetForm


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Ошибка регистрации')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Неверный логин или пароль')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def logout_view(request):
    referer = request.META.get('HTTP_REFERER', '/')
    if '/my-rent' in referer:
        referer = '/'
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта.')
    return redirect(referer)


def simple_password_reset_view(request):
    if request.method == 'POST':
        form = SimplePasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пароль успешно обновлён.')
        else:
            messages.error(request, 'Ошибка при восстановлении пароля.')

    return redirect(request.META.get('HTTP_REFERER', '/'))
