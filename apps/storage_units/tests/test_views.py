from decimal import Decimal

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.orders.models import CostCalculationRequest
from apps.storage_units.models import Tariff, Warehouse

NEW_PASSWORD = "Brand-New-Pass-98765"


def _texts(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


# --- главная ----------------------------------------------------------------


def test_главная_показывает_данные_ближайшего_склада(client, warehouse, make_box):
    warehouse.is_default_nearest = True
    warehouse.temperature = Decimal("15.5")
    warehouse.save()
    make_box(price="1200.00")
    make_box(price="1300.00", is_free=False)

    response = client.get(reverse("storage_units:index"))

    data = response.context["warehouse"]
    assert data["name"] == "Центральный"
    assert data["total_boxes"] == 2
    assert data["free_boxes"] == 1
    assert data["monthly_cost"] == "1200.00 ₽"
    assert data["temperature"] == "15.5 °С"


def test_главная_без_складов_открывается(client, db):
    response = client.get(reverse("storage_units:index"))

    assert response.status_code == 200
    assert response.context["warehouse"] == {}


def test_главная_без_свободных_боксов_берёт_цену_любого_бокса(
    client, warehouse, make_box
):
    make_box(price="900.00", is_free=False)

    data = client.get(reverse("storage_units:index")).context["warehouse"]

    assert data["monthly_cost"] == "900.00 ₽"
    assert data["temperature"] == "Неизвестно"


def test_главная_склад_без_боксов_просит_уточнить_цену(client, warehouse):
    data = client.get(reverse("storage_units:index")).context["warehouse"]

    assert data["monthly_cost"] == "Цену уточняйте"


def test_главная_при_нескольких_ближайших_складах_не_падает(client, warehouse):
    warehouse.is_default_nearest = True
    warehouse.save()
    Warehouse.objects.create(
        name="Второй", address="Адрес", ceilings=3, is_default_nearest=True
    )

    response = client.get(reverse("storage_units:index"))

    assert response.status_code == 200
    assert response.context["warehouse"]["name"]


# --- боксы и тарифы ---------------------------------------------------------


def test_список_боксов_считает_свободные(client, warehouse, make_box):
    make_box()
    make_box()
    make_box(is_free=False)

    response = client.get(reverse("storage_units:boxes_list"))

    item = response.context["warehouses"].get(pk=warehouse.pk)
    assert item.total_boxes_count == 3
    assert item.free_boxes_count == 2


def test_страница_тарифов_показывает_тарифы_по_площади(client, db):
    Tariff.objects.create(name="Большой", price=5000, min_square_meters=10)
    Tariff.objects.create(name="Малый", price=1000, min_square_meters=1)

    response = client.get(reverse("storage_units:tariffs"))

    names = [tariff.name for tariff in response.context["tariffs"]]
    assert names == ["Малый", "Большой"]


# --- заявка на расчёт стоимости ---------------------------------------------


def test_заявка_на_расчёт_сохраняется_и_ведёт_на_подтверждение(client, db):
    response = client.post(
        reverse("storage_units:submit_cost_request"), {"email": "lead@example.com"}
    )

    assert response.status_code == 302
    assert response.url == reverse("storage_units:cost_confirmation")
    assert CostCalculationRequest.objects.get().email == "lead@example.com"

    page = client.get(response.url)
    assert page.status_code == 200
    assert "lead@example.com" in page.content.decode()


def test_заявка_без_email_отклоняется(client, db):
    response = client.post(
        reverse("storage_units:submit_cost_request"),
        {"email": ""},
        HTTP_REFERER="/tariffs/",
    )

    assert response.url == "/tariffs/"
    assert not CostCalculationRequest.objects.exists()
    assert any("e-mail" in text for text in _texts(response))


def test_подтверждение_без_заявки_ведёт_на_главную(client, db):
    response = client.get(reverse("storage_units:cost_confirmation"))

    assert response.status_code == 302
    assert response.url == reverse("storage_units:index")


# --- личный кабинет ---------------------------------------------------------


def test_кабинет_показывает_только_свои_боксы(client, client_a, client_b, make_rental):
    mine = make_rental(client_a)
    make_rental(client_b)
    client.force_login(client_a.user)

    response = client.get(reverse("storage_units:my_rent"))

    assert [box.pk for box in response.context["boxes"]] == [mine.box.pk]
    assert response.context["boxes"][0].rental == mine


def test_смена_email_в_кабинете_обновляет_логин(client, client_a):
    client.force_login(client_a.user)

    client.post(reverse("storage_units:my_rent"), {"email": "new@example.com"})

    user = client_a.user
    user.refresh_from_db()
    assert user.email == "new@example.com"
    assert user.username == "new@example.com"


def test_смена_пароля_в_кабинете(client, client_a, password):
    client.force_login(client_a.user)

    response = client.post(
        reverse("storage_units:my_rent"),
        {
            "email": client_a.user.email,
            "old_password": password,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    user = client_a.user
    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)
    assert any("Пароль успешно обновлён" in text for text in _texts(response))


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {"old_password": "неверный", "new_password": "x", "confirm_password": "x"},
            "неверно",
        ),
        ({"new_password": "a", "confirm_password": "b"}, "не совпадают"),
        ({"new_password": "", "confirm_password": ""}, "не может быть пустым"),
    ],
)
def test_неверная_смена_пароля_в_кабинете_не_меняет_пароль(
    client, client_a, password, data, expected
):
    client.force_login(client_a.user)
    data = {"old_password": password, **data, "email": client_a.user.email}

    response = client.post(reverse("storage_units:my_rent"), data)

    user = client_a.user
    user.refresh_from_db()
    assert user.check_password(password)
    assert any(expected in text for text in _texts(response))
