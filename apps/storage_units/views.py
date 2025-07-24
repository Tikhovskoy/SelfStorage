from django.shortcuts import render
from .models import Warehouse, Box

def index(request):
    try:
        nearest_warehouse = Warehouse.objects.get(is_default_nearest=True)
    except Warehouse.DoesNotExist:
        nearest_warehouse = Warehouse.objects.first()
    except Warehouse.MultipleObjectsReturned:
        nearest_warehouse = Warehouse.objects.filter(is_default_nearest=True).first()

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
            'warehouse': warehouse_data
        }

    return render(request, 'index.html', context)


def boxes_list(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


def my_rent(request):
    # has_rent = False
    #
    # template_name = 'my-rent.html' if has_rent else 'my-rent-empty.html'
    # return render(request, template_name, {})
    return render(request, 'my-rent.html', {})


def my_rent_empty(requests):
    return render(requests, 'my-rent-empty.html', {})


def boxes(requests):
    return  render(requests, 'boxes.html', {})


def tariffs_view(requests):
    return render(requests, 'tariffs.html', {'title' : 'Тарифы'})

def calculate_cost_view(requests):
    return render(requests, 'calculate_cost', {'title': 'Рассчитать стоимость'})