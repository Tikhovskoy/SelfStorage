from django.shortcuts import render

def index(request):
    return render(request, 'index.html')


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
