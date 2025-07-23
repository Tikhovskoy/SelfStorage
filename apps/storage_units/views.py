from django.shortcuts import render

def index(request):
    return render(request, 'index.html')


def boxes_list(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


def my_rent(request):
    has_rent = False

    template_name = 'my_rent.html' if has_rent else 'my_rent_empty.html'
    return render(request, template_name)
