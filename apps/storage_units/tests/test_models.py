from decimal import Decimal

from django.core.management import call_command

from apps.promo.models import PromoCode
from apps.storage_units.models import Box, Tariff, Warehouse


def test_площадь_бокса_считается_при_сохранении(make_box):
    box = make_box(length=3, width=4)

    assert box.square == 12


def test_минимальная_цена_склада(warehouse, make_box):
    assert warehouse.min_tariff_price is None

    make_box(price="1500.00")
    make_box(price="900.00")

    assert warehouse.min_tariff_price == Decimal("900.00")


def test_строковые_представления(warehouse, make_box, client_a, make_rental):
    box = make_box()
    rental = make_rental(client_a)
    tariff = Tariff.objects.create(
        name="Малый", price=1000, min_square_meters=1, max_square_meters=3
    )
    open_tariff = Tariff.objects.create(
        name="Большой", price=5000, min_square_meters=10
    )

    assert str(warehouse) == "Склад Центральный"
    assert str(box) == f"№ бокса {box.id}"
    assert "1-3 м²" in str(tariff)
    assert "10-∞ м²" in str(open_tariff)
    assert str(rental.box.id) in str(rental)
    assert str(client_a) == "Анна"


def test_qr_код_аренды_создаётся_при_сохранении(client_a, make_rental):
    rental = make_rental(client_a)

    assert rental.qr_token
    assert rental.qr_code.name.startswith("qr_codes/qr_")


def test_команда_creation_boxes_создаёт_боксы_на_каждом_складе(warehouse):
    call_command("creation_boxes")

    count = Box.objects.filter(warehouse=warehouse).count()
    assert 130 <= count <= 390
    assert Warehouse.objects.count() == 1


def test_админка_промокодов_считает_клиентов(client_a, make_promo):
    from django.contrib import admin

    promo = make_promo()
    promo.used_clients.add(client_a)
    model_admin = admin.site._registry[PromoCode]

    assert model_admin.used_clients_count(promo) == 1
