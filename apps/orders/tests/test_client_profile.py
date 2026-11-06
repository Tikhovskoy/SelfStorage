from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse

from apps.orders.models import Client
from apps.storage_units.models import Box


def test_при_создании_пользователя_создаётся_профиль_клиента(db):
    user = User.objects.create_user(
        "new@example.com",
        "new@example.com",
        "StrongPass-12345",
        first_name="Олег",
        last_name="Петров",
    )

    profile = Client.objects.get(user=user)
    assert profile.first_name == "Олег"
    assert profile.last_name == "Петров"
    assert profile.email == "new@example.com"


def test_суперпользователь_тоже_получает_профиль(db):
    admin = User.objects.create_superuser("admin", "admin@example.com", "pass-12345")

    assert Client.objects.filter(user=admin).count() == 1


def test_повторное_сохранение_пользователя_не_дублирует_профиль(db):
    user = User.objects.create_user("u@example.com", "u@example.com", "pass-12345")

    user.first_name = "Мария"
    user.save()

    assert Client.objects.filter(user=user).count() == 1


def test_регистрация_создаёт_ровно_один_профиль(client, db):
    response = client.post(
        reverse("storage_units:register"),
        {
            "first_name": "Ольга",
            "last_name": "Смирнова",
            "email": "olga@example.com",
            "password": "StrongPass-12345",
            "password_confirm": "StrongPass-12345",
        },
    )

    assert response.status_code == 302
    profiles = Client.objects.filter(user__username="olga@example.com")
    assert profiles.count() == 1
    assert profiles.get().first_name == "Ольга"


def test_админ_без_профиля_арендует_бокс_без_ошибки(client, make_box):
    admin = User.objects.create_superuser("admin", "admin@example.com", "pass-12345")
    Client.objects.filter(user=admin).delete()  # как у аккаунтов до появления сигнала
    box = make_box()
    client.force_login(admin)

    response = client.post(
        reverse("storage_units:rent_box", args=[box.id]),
        {"rent_until": (date.today() + timedelta(days=30)).isoformat()},
    )

    assert response.status_code == 302
    box = Box.objects.get(pk=box.pk)
    assert box.tenant.user == admin


def test_пользователь_без_профиля_открывает_личный_кабинет(client, db):
    user = User.objects.create_user("x@example.com", "x@example.com", "pass-12345")
    Client.objects.filter(user=user).delete()
    client.force_login(user)

    response = client.get(reverse("storage_units:my_rent"))

    assert response.status_code == 200
    assert Client.objects.filter(user=user).count() == 1
