from django.shortcuts import get_object_or_404, redirect

from .models import ShortLink


def short_redirect(request, token):
    link = get_object_or_404(ShortLink, token=token)
    link.click_count += 1
    link.save()
    return redirect(link.target_url)
