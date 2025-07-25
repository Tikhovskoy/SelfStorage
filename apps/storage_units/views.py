from django.shortcuts import render, get_object_or_404
from .models import Warehouse, Box, Tariff
from apps.orders.forms import RegistrationForm, LoginForm, ProfileForm, SimplePasswordResetForm
from apps.orders.models import Client
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import json
from apps.storage_units.models import Box


def index(request):
    try:
        nearest_warehouse = Warehouse.objects.get(is_default_nearest=True)
    except Warehouse.DoesNotExist:
        nearest_warehouse = Warehouse.objects.first()
    except Warehouse.MultipleObjectsReturned:
        nearest_warehouse = Warehouse.objects.filter(is_default_nearest=True).first()

    warehouse_data = {}
    if nearest_warehouse:
        total_boxes = nearest_warehouse.boxes.count()
        free_boxes = nearest_warehouse.boxes.filter(is_free=True).count()

        box_price = None
        first_free_box = nearest_warehouse.boxes.filter(is_free=True).first()
        if first_free_box:
            box_price = first_free_box.price
        else:
            any_box = nearest_warehouse.boxes.first()
            if any_box:
                box_price = any_box.price

        display_monthly_cost = f"{box_price} ₽" if box_price is not None else 'Цену уточняйте'

        warehouse_data = {
            'name': nearest_warehouse.name,
            'address': nearest_warehouse.address,
            'temperature': f"{nearest_warehouse.temperature} °С" if nearest_warehouse.temperature is not None else 'Неизвестно',
            'ceiling_height': f"до {nearest_warehouse.ceilings} м",
            'monthly_cost': display_monthly_cost,
            'total_boxes': total_boxes,
            'free_boxes': free_boxes,
        }

    form_data = request.session.pop('reset_form_data', None)
    form_errors_json = request.session.pop('reset_form_errors', None)

    if form_data:
        reset_form = SimplePasswordResetForm(form_data)
        if form_errors_json:
            form_errors = json.loads(form_errors_json)
            for field, errors in form_errors.items():
                for error in errors:
                    reset_form.add_error(field, error.get('message'))
    else:
        reset_form = SimplePasswordResetForm()

    context = {
        'warehouse': warehouse_data,
        'registration_form': RegistrationForm(),
        'login_form': LoginForm(),
        'reset_form': reset_form,
    }

    return render(request, 'index.html', context)


def boxes_list(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


@login_required
def my_rent(request):
    client = get_object_or_404(Client, user=request.user)
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()

            new_email = form.cleaned_data.get('email')
            if new_email and new_email != user.email:
                user.email = new_email
                user.username = new_email
                user.save()

            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if old_password or new_password or confirm_password:
                if not user.check_password(old_password):
                    messages.error(request, 'Старый пароль введён неверно.')
                elif new_password != confirm_password:
                    messages.error(request, 'Новый пароль и подтверждение не совпадают.')
                elif not new_password:
                    messages.error(request, 'Новый пароль не может быть пустым.')
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Пароль успешно обновлён.')
    else:
        form = ProfileForm(instance=client)

    boxes = Box.objects.filter(tenant=client)

    context = {
        'client': client,
        'form': form,
        'boxes': boxes,
    }

    return render(request, 'my-rent.html', context)


def my_rent_empty(requests):
    return render(requests, 'my-rent-empty.html', {})


def boxes(requests):
    return  render(requests, 'boxes.html', {})


def tariffs_view(requests):
    tariffs = Tariff.objects.all().order_by('min_square_meters')
    context = {
        'tariffs': tariffs
    }
    return render(requests, 'tariffs.html', context)

def calculate_cost_view(requests):
    return render(requests, 'calculate_cost', {'title': 'Рассчитать стоимость'})