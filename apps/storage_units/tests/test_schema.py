from django.core.management import call_command

from apps.storage_units.models import Warehouse


def test_модели_не_расходятся_с_миграциями(db):
    # при расхождении команда завершается с кодом 1 (SystemExit)
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


def test_варианты_преимуществ_склада_упорядочены():
    assert isinstance(Warehouse.ADVANTAGE_CHOICE, (list, tuple))
