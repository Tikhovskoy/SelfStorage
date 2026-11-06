from django.core.management import call_command

from apps.storage_units.models import Warehouse


def test_модели_не_расходятся_с_миграциями(db):
    # при расхождении команда завершается с кодом 1 (SystemExit)
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


def test_варианты_преимуществ_склада_упорядочены():
    assert isinstance(Warehouse.ADVANTAGE_CHOICE, (list, tuple))


def test_у_аренды_есть_итоговая_цена_и_скидка(client_a, make_rental):
    rental = make_rental(client_a)

    assert rental.price is None
    assert rental.discount_percent == 0
