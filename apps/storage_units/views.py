from django.shortcuts import render

def index(request):
    nearest_warehouse = {
        'name': 'Склад SelfStorage на Пушкина',
        'address': 'г. Москва, ул. Пушкина, 37',
        'temperature': '18 °С',
        'free_boxes': '24 из 258',
        'ceiling_height': 'до 3.5 м',
        'monthly_cost': '2264 ₽',
        'has_delivery': True,
    }

    context = {
        'title': 'SelfStorage – Удобное и бережное хранение ваших вещей',
        'warehouse': nearest_warehouse,
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
