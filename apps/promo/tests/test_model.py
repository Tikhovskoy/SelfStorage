from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from unittest.mock import patch

from django.utils import timezone


def test_действующий_промокод_активен(make_promo):
    assert make_promo().is_active()


def test_истёкший_промокод_неактивен(make_promo):
    promo = make_promo(active_to=timezone.localdate() - timedelta(days=1))

    assert not promo.is_active()


def test_ещё_не_начавшийся_промокод_неактивен(make_promo):
    promo = make_promo(active_from=timezone.localdate() + timedelta(days=1))

    assert not promo.is_active()


def test_в_последний_день_действия_промокод_активен(make_promo):
    today = timezone.localdate()

    assert make_promo(active_from=today, active_to=today).is_active()


def test_дата_действия_считается_по_местному_времени(make_promo):
    # 22:30 UTC 6 ноября — это уже 7 ноября, 01:30 по Москве
    promo = make_promo(active_from=date(2026, 11, 7), active_to=date(2026, 11, 7))
    moment = datetime(2026, 11, 6, 22, 30, tzinfo=dt_timezone.utc)

    with patch("django.utils.timezone.now", return_value=moment):
        assert promo.is_active()


def test_исчерпанный_лимит_делает_промокод_неактивным(make_promo):
    promo = make_promo(usage_limit=2, used_count=2)

    assert not promo.is_active()


def test_одноразовый_промокод_неактивен_для_того_же_клиента(make_promo, client_a):
    promo = make_promo(one_time_per_user=True)
    promo.used_clients.add(client_a)

    assert not promo.is_active(client=client_a)
