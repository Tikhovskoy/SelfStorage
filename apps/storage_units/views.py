from django.shortcuts import render, get_object_or_404
from .models import Warehouse, Box
from apps.orders.forms import RegistrationForm, LoginForm, ProfileForm
from apps.orders.models import Client
from django.contrib.auth.decorators import login_required

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

    context = {
        'warehouse': warehouse_data,
        'registration_form': RegistrationForm(),
        'login_form': LoginForm(),
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

    else:
        form = ProfileForm(instance=client)

    context = {
        'client': client,
        'form': form,
    }

    return render(request, 'my-rent.html', context)


def my_rent_empty(requests):
    return render(requests, 'my-rent-empty.html', {})


def boxes(requests):
    return  render(requests, 'boxes.html', {})


def tariffs_view(requests):
    return render(requests, 'tariffs.html', {'title' : 'Тарифы'})

def calculate_cost_view(requests):
    return render(requests, 'calculate_cost', {'title': 'Рассчитать стоимость'})