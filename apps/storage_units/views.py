from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.orders.forms import LoginForm, ProfileForm, RegistrationForm
from apps.orders.models import CostCalculationRequest
from apps.orders.services import ensure_client
from apps.promo.services import PromoError, redeem_promo
from apps.storage_units.models import Rental

from .models import Box, Tariff, Warehouse


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

        display_monthly_cost = (
            f"{box_price} ₽" if box_price is not None else "Цену уточняйте"
        )

        warehouse_data = {
            "name": nearest_warehouse.name,
            "address": nearest_warehouse.address,
            "temperature": (
                f"{nearest_warehouse.temperature} °С"
                if nearest_warehouse.temperature is not None
                else "Неизвестно"
            ),
            "ceiling_height": f"до {nearest_warehouse.ceilings} м",
            "monthly_cost": display_monthly_cost,
            "total_boxes": total_boxes,
            "free_boxes": free_boxes,
        }

    context = {
        "warehouse": warehouse_data,
        "registration_form": RegistrationForm(),
        "login_form": LoginForm(),
    }

    return render(request, "index.html", context)


def boxes_list(request):
    return render(request, "boxes.html")


def faq(request):
    return render(request, "faq.html")


@login_required
def my_rent(request):
    client = ensure_client(request.user)
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()

            new_email = form.cleaned_data.get("email")
            if new_email and new_email != user.email:
                user.email = new_email
                user.username = new_email
                user.save()

            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if old_password or new_password or confirm_password:
                if not user.check_password(old_password):
                    messages.error(request, "Старый пароль введён неверно.")
                elif new_password != confirm_password:
                    messages.error(
                        request, "Новый пароль и подтверждение не совпадают."
                    )
                elif not new_password:
                    messages.error(request, "Новый пароль не может быть пустым.")
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Пароль успешно обновлён.")
    else:
        form = ProfileForm(instance=client)

    boxes = Box.objects.filter(tenant=client)
    for box in boxes:
        box.rental = Rental.objects.filter(box=box).first()

    context = {
        "client": client,
        "form": form,
        "boxes": boxes,
    }

    return render(request, "my-rent.html", context)


def my_rent_empty(request):
    return render(request, "my-rent-empty.html", {})


def tariffs_view(request):
    tariffs = Tariff.objects.all().order_by("min_square_meters")
    context = {"tariffs": tariffs}
    return render(request, "tariffs.html", context)


def calculate_cost_view(request):
    return render(request, "calculate_cost", {"title": "Рассчитать стоимость"})


def boxes_list_view(request):
    warehouses = Warehouse.objects.annotate(
        total_boxes_count=Count("boxes"),
        free_boxes_count=Count("boxes", filter=Q(boxes__is_free=True)),
    )

    context = {
        "title": "Наши боксы",
        "warehouses": warehouses,
    }
    return render(request, "boxes.html", context)


def _parse_date(request, raw_value):
    """Разбирает дату из формы; при ошибке сообщает пользователю и даёт None."""
    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Неверный формат даты.")
        return None


def _apply_promo(request, client, code, box):
    """Применяет промокод; если он не подходит, предупреждает и берёт полную цену."""
    try:
        return redeem_promo(client, code, box)
    except PromoError as error:
        messages.warning(request, str(error))
        return redeem_promo(client, "", box)


@require_POST
@login_required
def renew_box(request, box_id):
    client = ensure_client(request.user)
    # продлевать можно только бокс, арендованный текущим клиентом, иначе 404
    get_object_or_404(Rental, box_id=box_id, client=client)

    renew_date = request.POST.get("renew_date")
    promo_code = request.POST.get("promo_code", "")

    if renew_date:
        new_end_date = _parse_date(request, renew_date)
        if new_end_date is None:
            return redirect("storage_units:my_rent")

        with transaction.atomic():
            rental = get_object_or_404(
                Rental.objects.select_for_update().select_related("box"),
                box_id=box_id,
                client=client,
            )
            box = rental.box
            result = _apply_promo(request, client, promo_code, box)

            box.paid_for = new_end_date
            box.is_free = False
            box.save()

            rental.end_date = new_end_date
            rental.price = result.price
            rental.discount_percent = result.discount_percent
            rental.save()

        if result.discount_percent:
            messages.success(
                request, f"Аренда продлена со скидкой {result.discount_percent}%."
            )
        else:
            messages.success(request, "Аренда продлена.")

    return redirect("storage_units:my_rent")


@require_POST
@login_required
def rent_box(request, box_id):
    client = ensure_client(request.user)
    rent_until = request.POST.get("rent_until")
    promo_code = request.POST.get("promo_code", "")

    rent_until_date = None
    if rent_until:
        rent_until_date = _parse_date(request, rent_until)
        if rent_until_date is None:
            return redirect("storage_units:boxes_list")

    with transaction.atomic():
        # блокировка строки не даёт двум клиентам одновременно занять один бокс
        box = get_object_or_404(Box.objects.select_for_update(), id=box_id)

        if box.tenant is not None:
            messages.warning(request, "Этот бокс уже занят.")
        elif rent_until_date is not None:
            result = _apply_promo(request, client, promo_code, box)

            box.tenant = client
            box.paid_for = rent_until_date
            box.is_free = False
            box.save()

            Rental.objects.create(
                client=client,
                box=box,
                end_date=rent_until_date,
                price=result.price,
                discount_percent=result.discount_percent,
            )

            if result.discount_percent:
                messages.success(
                    request,
                    f"Вы арендовали бокс со скидкой {result.discount_percent}%.",
                )
            else:
                messages.success(request, "Бокс успешно арендован.")

    return redirect("storage_units:my_rent")


@require_POST
def handle_email_cost_request(request):
    email = request.POST.get("email")
    if email:
        CostCalculationRequest.objects.create(email=email)
        request.session["last_email"] = email
        request.session["estimated_cost"] = "от 190 ₽ за м²"
        return redirect("storage_units:cost_confirmation")
    else:
        messages.error(request, "Пожалуйста, укажите корректный e-mail.")
        return redirect(request.META.get("HTTP_REFERER", "/"))


def cost_confirmation(request):
    email = request.session.pop("last_email", None)
    cost = request.session.pop("estimated_cost", None)

    if not email or not cost:
        return redirect("storage_units:index")

    context = {
        "email": email,
        "estimated_cost": cost,
    }
    return render(request, "cost_confirmation.html", context)


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"
