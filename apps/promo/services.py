from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import F

from .models import PromoCode

CENT = Decimal("0.01")


class PromoError(Exception):
    """Промокод нельзя применить; текст ошибки можно показать пользователю."""


@dataclass(frozen=True)
class PromoResult:
    """Итог применения промокода к боксу."""

    price: Decimal
    discount_percent: int
    promo: PromoCode | None = None


def calculate_price(base_price, discount_percent):
    """Цена со скидкой, округлённая до копеек. Скидка ограничена 0–100%."""
    percent = max(0, min(int(discount_percent), 100))
    price = Decimal(base_price) * (100 - percent) / 100
    return price.quantize(CENT, rounding=ROUND_HALF_UP)


def consume_promo(promo, client):
    """Списывает одно использование промокода.

    Счётчик увеличивается на стороне БД (F-выражение), поэтому параллельные
    запросы не теряют списания, даже если объект promo уже устарел.
    """
    PromoCode.objects.filter(pk=promo.pk).update(used_count=F("used_count") + 1)
    promo.used_clients.add(client)


def _find_promo(code):
    candidates = PromoCode.objects.select_for_update().filter(code__iexact=code)
    # коды уникальны с учётом регистра, поэтому сначала ищем точное совпадение
    promo = candidates.filter(code=code).first() or candidates.first()
    if promo is None:
        raise PromoError("Промокод не найден.")
    return promo


@transaction.atomic
def redeem_promo(client, code, box):
    """Применяет промокод к боксу и возвращает итоговую цену.

    Без кода возвращает полную цену бокса и ничего не списывает. Если код
    нельзя применить, бросает PromoError, и ничего не списывается.

    Использование списывается сразу, поэтому вызывать функцию нужно в одной
    транзакции с созданием или продлением аренды: при ошибке аренды откатится
    и списание. Строка промокода блокируется на время транзакции, чтобы
    проверка лимита и «один раз на клиента» не обходилась параллельными
    запросами.
    """
    code = (code or "").strip()
    if not code:
        return PromoResult(price=calculate_price(box.price, 0), discount_percent=0)

    promo = _find_promo(code)
    if not promo.is_active(client=client):
        raise PromoError("Промокод недействителен или уже использован.")

    consume_promo(promo, client)
    percent = min(promo.discount_percent, 100)
    return PromoResult(
        price=calculate_price(box.price, percent),
        discount_percent=percent,
        promo=promo,
    )
