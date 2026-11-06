from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from apps.orders.models import Client
from apps.storage_units.models import Box, Rental, Warehouse

PASSWORD = "StrongPass-12345"


@pytest.fixture
def password():
    return PASSWORD


@pytest.fixture(autouse=True)
def _tmp_media_root(settings, tmp_path):
    """QR-коды аренд пишутся во временную папку, а не в media/ проекта."""
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def make_client(db):
    """Фабрика клиентов: создаёт пользователя и привязанный профиль Client."""

    def factory(email="client@example.com", first_name="Иван", password=PASSWORD):
        user = User.objects.create_user(
            username=email, email=email, password=password, first_name=first_name
        )
        client, _ = Client.objects.get_or_create(
            user=user, defaults={"first_name": first_name, "email": email}
        )
        return client

    return factory


@pytest.fixture
def client_a(make_client):
    return make_client("a@example.com", "Анна")


@pytest.fixture
def client_b(make_client):
    return make_client("b@example.com", "Борис")


@pytest.fixture
def warehouse(db):
    return Warehouse.objects.create(
        name="Центральный", address="Москва, ул. Складская, 1", ceilings=3
    )


@pytest.fixture
def make_box(warehouse):
    """Фабрика боксов; по умолчанию бокс свободен, цена 1000 ₽."""

    def factory(price="1000.00", **extra):
        defaults = dict(
            warehouse=warehouse, floor=1, length=2, width=2, height=Decimal("2.5")
        )
        defaults.update(extra, price=Decimal(price))
        return Box.objects.create(**defaults)

    return factory


@pytest.fixture
def future_date():
    """Дата окончания аренды в будущем в формате, который шлёт форма."""
    return (date.today() + timedelta(days=30)).isoformat()


@pytest.fixture
def make_rental(make_box):
    """Фабрика аренд: занимает бокс клиентом и создаёт Rental."""

    def factory(client, box=None, end_date=None, **box_kwargs):
        box = box or make_box(**box_kwargs)
        end_date = end_date or date.today() + timedelta(days=10)
        box.tenant = client
        box.is_free = False
        box.paid_for = end_date
        box.save()
        return Rental.objects.create(client=client, box=box, end_date=end_date)

    return factory
