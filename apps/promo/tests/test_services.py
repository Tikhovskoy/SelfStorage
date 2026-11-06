from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.promo.models import PromoCode
from apps.promo.services import (
    PromoError,
    calculate_price,
    consume_promo,
    redeem_promo,
)


@pytest.mark.parametrize(
    ("base", "percent", "expected"),
    [
        ("1000.00", 10, "900.00"),
        ("1000.00", 0, "1000.00"),
        ("1000.00", 100, "0.00"),
        ("1000.00", 150, "0.00"),  # скидка не может превысить 100%
        ("199.99", 15, "169.99"),  # округление до копеек
        ("100.05", 33, "67.03"),
    ],
)
def test_расчёт_цены_со_скидкой(base, percent, expected):
    assert calculate_price(Decimal(base), percent) == Decimal(expected)


def test_без_кода_возвращается_полная_цена_и_ничего_не_списывается(
    client_a, make_box, make_promo
):
    promo = make_promo()

    result = redeem_promo(client_a, "", make_box())

    assert result.price == Decimal("1000.00")
    assert result.discount_percent == 0
    assert result.promo is None
    promo.refresh_from_db()
    assert promo.used_count == 0


def test_промокод_даёт_скидку_от_цены_бокса(client_a, make_box, make_promo):
    promo = make_promo(discount_percent=25)
    box = make_box(price="2000.00")

    result = redeem_promo(client_a, "SUMMER10", box)

    assert result.price == Decimal("1500.00")
    assert result.discount_percent == 25
    box.refresh_from_db()
    assert box.price == Decimal("2000.00")  # цена бокса не меняется
    promo.refresh_from_db()
    assert promo.used_count == 1
    assert list(promo.used_clients.all()) == [client_a]


def test_код_ищется_без_учёта_регистра_и_пробелов(client_a, make_box, make_promo):
    make_promo(code="SUMMER10")

    result = redeem_promo(client_a, "  summer10 ", make_box())

    assert result.discount_percent == 10


def test_неизвестный_код(client_a, make_box):
    with pytest.raises(PromoError, match="не найден"):
        redeem_promo(client_a, "NOPE", make_box())


def test_истёкший_промокод_не_применяется_и_не_списывается(
    client_a, make_box, make_promo
):
    today = timezone.localdate()
    promo = make_promo(
        active_from=today - timedelta(days=10), active_to=today - timedelta(days=1)
    )

    with pytest.raises(PromoError, match="недействителен"):
        redeem_promo(client_a, promo.code, make_box())

    promo.refresh_from_db()
    assert promo.used_count == 0
    assert not promo.used_clients.exists()


def test_лимит_использований(client_a, client_b, make_box, make_promo):
    promo = make_promo(usage_limit=1)

    redeem_promo(client_a, promo.code, make_box())
    with pytest.raises(PromoError):
        redeem_promo(client_b, promo.code, make_box())

    promo.refresh_from_db()
    assert promo.used_count == 1
    assert list(promo.used_clients.all()) == [client_a]


def test_один_раз_на_клиента(client_a, client_b, make_box, make_promo):
    promo = make_promo(one_time_per_user=True)

    redeem_promo(client_a, promo.code, make_box())
    with pytest.raises(PromoError):
        redeem_promo(client_a, promo.code, make_box())
    redeem_promo(client_b, promo.code, make_box())  # другому клиенту можно

    promo.refresh_from_db()
    assert promo.used_count == 2


def test_без_ограничения_клиент_применяет_промокод_повторно(
    client_a, make_box, make_promo
):
    promo = make_promo(one_time_per_user=False)

    redeem_promo(client_a, promo.code, make_box())
    redeem_promo(client_a, promo.code, make_box())

    promo.refresh_from_db()
    assert promo.used_count == 2


def test_списание_не_теряется_при_устаревшем_объекте(client_a, make_promo):
    """used_count растёт на стороне БД: параллельный запрос не затирает чужое."""
    promo = make_promo()
    stale = PromoCode.objects.get(pk=promo.pk)  # копия, прочитанная «до»
    PromoCode.objects.filter(pk=promo.pk).update(used_count=5)  # чужое списание

    consume_promo(stale, client_a)

    promo.refresh_from_db()
    assert promo.used_count == 6


def test_скидка_выше_100_процентов_даёт_нулевую_цену(client_a, make_box, make_promo):
    promo = make_promo(discount_percent=150)

    result = redeem_promo(client_a, promo.code, make_box())

    assert result.price == Decimal("0.00")
    assert result.discount_percent == 100
