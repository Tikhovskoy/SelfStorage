from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from apps.storage_units.models import Box, Rental

RENT_UNTIL = (date.today() + timedelta(days=30)).isoformat()
RENEW_UNTIL = (date.today() + timedelta(days=60)).isoformat()


def _rent(client, box, **data):
    return client.post(reverse("storage_units:rent_box", args=[box.id]), data)


def _renew(client, box, **data):
    return client.post(reverse("storage_units:renew_box", args=[box.id]), data)


def _texts(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


@pytest.fixture
def logged_a(client, client_a):
    client.force_login(client_a.user)
    return client


# --- аренда -----------------------------------------------------------------


def test_аренда_со_скидкой_сохраняет_итоговую_цену(
    logged_a, client_a, make_box, make_promo
):
    promo = make_promo(discount_percent=10)
    box = make_box(price="1000.00")

    response = _rent(logged_a, box, rent_until=RENT_UNTIL, promo_code=promo.code)

    assert response.status_code == 302
    rental = Rental.objects.get(box=box)
    assert rental.client == client_a
    assert rental.price == Decimal("900.00")
    assert rental.discount_percent == 10
    box.refresh_from_db()
    assert box.price == Decimal("1000.00")
    assert box.tenant == client_a
    promo.refresh_from_db()
    assert promo.used_count == 1
    assert client_a in promo.used_clients.all()


def test_аренда_без_промокода_по_полной_цене(logged_a, make_box):
    box = make_box(price="1500.00")

    _rent(logged_a, box, rent_until=RENT_UNTIL)

    rental = Rental.objects.get(box=box)
    assert rental.price == Decimal("1500.00")
    assert rental.discount_percent == 0


def test_без_даты_аренды_промокод_не_списывается(logged_a, make_box, make_promo):
    promo = make_promo()
    box = make_box()

    _rent(logged_a, box, promo_code=promo.code)

    promo.refresh_from_db()
    assert promo.used_count == 0
    assert not promo.used_clients.exists()
    assert not Rental.objects.exists()
    box.refresh_from_db()
    assert box.tenant is None


def test_при_неверной_дате_промокод_не_списывается(logged_a, make_box, make_promo):
    promo = make_promo()
    box = make_box()

    _rent(logged_a, box, rent_until="не дата", promo_code=promo.code)

    promo.refresh_from_db()
    assert promo.used_count == 0
    assert not Rental.objects.exists()


def test_занятый_бокс_не_арендуется_и_промокод_не_списывается(
    client, client_a, client_b, make_rental, make_promo
):
    rental = make_rental(client_a)
    promo = make_promo()
    client.force_login(client_b.user)

    _rent(client, rental.box, rent_until=RENT_UNTIL, promo_code=promo.code)

    promo.refresh_from_db()
    assert promo.used_count == 0
    rental.refresh_from_db()
    assert rental.client == client_a


def test_истёкший_промокод_аренда_идёт_без_скидки(logged_a, make_box, make_promo):
    today = timezone.localdate()
    promo = make_promo(
        active_from=today - timedelta(days=10), active_to=today - timedelta(days=1)
    )
    box = make_box(price="1000.00")

    response = _rent(logged_a, box, rent_until=RENT_UNTIL, promo_code=promo.code)

    rental = Rental.objects.get(box=box)
    assert rental.price == Decimal("1000.00")
    assert rental.discount_percent == 0
    promo.refresh_from_db()
    assert promo.used_count == 0
    assert any("недействителен" in text for text in _texts(response))


def test_несуществующий_промокод_аренда_идёт_без_скидки(logged_a, make_box):
    box = make_box(price="1000.00")

    response = _rent(logged_a, box, rent_until=RENT_UNTIL, promo_code="NOPE")

    assert Rental.objects.get(box=box).price == Decimal("1000.00")
    assert any("не найден" in text for text in _texts(response))


def test_лимит_использований_промокода(
    client, client_a, client_b, make_box, make_promo
):
    promo = make_promo(usage_limit=1)
    first, second = make_box(), make_box()

    client.force_login(client_a.user)
    _rent(client, first, rent_until=RENT_UNTIL, promo_code=promo.code)
    client.force_login(client_b.user)
    _rent(client, second, rent_until=RENT_UNTIL, promo_code=promo.code)

    assert Rental.objects.get(box=first).discount_percent == 10
    assert Rental.objects.get(box=second).discount_percent == 0
    promo.refresh_from_db()
    assert promo.used_count == 1


def test_промокод_один_раз_на_клиента(logged_a, make_box, make_promo):
    promo = make_promo(one_time_per_user=True)
    first, second = make_box(), make_box()

    _rent(logged_a, first, rent_until=RENT_UNTIL, promo_code=promo.code)
    _rent(logged_a, second, rent_until=RENT_UNTIL, promo_code=promo.code)

    assert Rental.objects.get(box=first).discount_percent == 10
    assert Rental.objects.get(box=second).discount_percent == 0
    promo.refresh_from_db()
    assert promo.used_count == 1


def test_ошибка_при_создании_аренды_откатывает_списание(
    client, client_a, make_box, make_promo, monkeypatch
):
    promo = make_promo()
    box = make_box()
    client.force_login(client_a.user)
    client.raise_request_exception = False

    def broken_create(*args, **kwargs):
        raise RuntimeError("сбой при создании аренды")

    monkeypatch.setattr(Rental.objects, "create", broken_create)

    response = _rent(client, box, rent_until=RENT_UNTIL, promo_code=promo.code)

    assert response.status_code == 500
    promo.refresh_from_db()
    assert promo.used_count == 0
    assert not promo.used_clients.exists()
    box = Box.objects.get(pk=box.pk)
    assert box.tenant is None


# --- продление --------------------------------------------------------------


def test_продление_со_скидкой_обновляет_цену(
    logged_a, client_a, make_rental, make_promo
):
    rental = make_rental(client_a, price="2000.00")
    promo = make_promo(discount_percent=20)

    response = _renew(
        logged_a, rental.box, renew_date=RENEW_UNTIL, promo_code=promo.code
    )

    assert response.status_code == 302
    rental.refresh_from_db()
    assert rental.end_date.isoformat() == RENEW_UNTIL
    assert rental.price == Decimal("1600.00")
    assert rental.discount_percent == 20
    promo.refresh_from_db()
    assert promo.used_count == 1
    assert client_a in promo.used_clients.all()


def test_продление_без_промокода_по_полной_цене(logged_a, client_a, make_rental):
    rental = make_rental(client_a, price="2000.00")

    _renew(logged_a, rental.box, renew_date=RENEW_UNTIL)

    rental.refresh_from_db()
    assert rental.price == Decimal("2000.00")
    assert rental.discount_percent == 0


def test_без_даты_продления_промокод_не_списывается(
    logged_a, client_a, make_rental, make_promo
):
    rental = make_rental(client_a)
    old_end = rental.end_date
    promo = make_promo()

    _renew(logged_a, rental.box, promo_code=promo.code)

    promo.refresh_from_db()
    assert promo.used_count == 0
    rental.refresh_from_db()
    assert rental.end_date == old_end


def test_неверная_дата_продления_не_падает_и_не_списывает_промокод(
    logged_a, client_a, make_rental, make_promo
):
    rental = make_rental(client_a)
    old_end = rental.end_date
    promo = make_promo()

    response = _renew(logged_a, rental.box, renew_date="не дата", promo_code=promo.code)

    assert response.status_code == 302
    promo.refresh_from_db()
    assert promo.used_count == 0
    rental.refresh_from_db()
    assert rental.end_date == old_end


def test_истёкший_промокод_при_продлении(logged_a, client_a, make_rental, make_promo):
    today = timezone.localdate()
    rental = make_rental(client_a, price="1000.00")
    promo = make_promo(
        active_from=today - timedelta(days=10), active_to=today - timedelta(days=1)
    )

    _renew(logged_a, rental.box, renew_date=RENEW_UNTIL, promo_code=promo.code)

    rental.refresh_from_db()
    assert rental.end_date.isoformat() == RENEW_UNTIL
    assert rental.price == Decimal("1000.00")
    assert rental.discount_percent == 0
    promo.refresh_from_db()
    assert promo.used_count == 0


def test_ошибка_при_продлении_откатывает_списание(
    client, client_a, make_rental, make_promo, monkeypatch
):
    rental = make_rental(client_a)
    old_end = rental.end_date
    promo = make_promo()
    client.force_login(client_a.user)
    client.raise_request_exception = False

    def broken_save(self, *args, **kwargs):
        raise RuntimeError("сбой при сохранении аренды")

    monkeypatch.setattr(Rental, "save", broken_save)

    response = _renew(client, rental.box, renew_date=RENEW_UNTIL, promo_code=promo.code)

    assert response.status_code == 500
    promo.refresh_from_db()
    assert promo.used_count == 0
    assert not promo.used_clients.exists()
    assert Rental.objects.get(pk=rental.pk).end_date == old_end
