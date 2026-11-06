import pytest
from django.urls import reverse

EVIL = [
    "https://evil.example",
    "https://evil.example/phish/",
    "//evil.example/phish/",
    "http://evil.example",
    "javascript:alert(1)",
    "///evil.example",
]

REGISTRATION = {
    "first_name": "Ольга",
    "last_name": "Смирнова",
    "email": "olga@example.com",
    "password": "StrongPass-12345",
    "password_confirm": "StrongPass-12345",
}


def _login_data(client_a, password, **extra):
    return {"username": client_a.user.username, "password": password, **extra}


@pytest.mark.parametrize("target", EVIL)
def test_вход_не_перенаправляет_на_чужой_адрес(client, client_a, password, target):
    response = client.post(
        reverse("storage_units:login"), _login_data(client_a, password, next=target)
    )

    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.parametrize("target", EVIL)
def test_регистрация_не_перенаправляет_на_чужой_адрес(client, db, target):
    response = client.post(
        reverse("storage_units:register"), {**REGISTRATION, "next": target}
    )

    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.parametrize("target", EVIL)
def test_выход_не_перенаправляет_на_чужой_referer(client, client_a, target):
    client.force_login(client_a.user)

    response = client.get(reverse("storage_units:logout"), HTTP_REFERER=target)

    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.parametrize("target", EVIL)
def test_неудачный_вход_не_уводит_на_чужой_referer(client, db, target):
    response = client.post(
        reverse("storage_units:login"),
        {"username": "nobody", "password": "wrong"},
        HTTP_REFERER=target,
    )

    assert response.status_code == 302
    assert response.url == "/"


def test_вход_с_чужим_next_использует_безопасный_referer(client, client_a, password):
    response = client.post(
        reverse("storage_units:login"),
        _login_data(client_a, password, next="https://evil.example"),
        HTTP_REFERER="http://testserver/faq/",
    )

    assert response.url == "http://testserver/faq/"


@pytest.mark.parametrize("target", ["/boxes/", "/faq/?a=1", "http://testserver/boxes/"])
def test_вход_разрешает_переход_на_свой_сайт(client, client_a, password, target):
    response = client.post(
        reverse("storage_units:login"), _login_data(client_a, password, next=target)
    )

    assert response.url == target


def test_регистрация_разрешает_переход_на_свой_сайт(client, db):
    response = client.post(
        reverse("storage_units:register"), {**REGISTRATION, "next": "/boxes/"}
    )

    assert response.url == "/boxes/"


def test_выход_возвращает_на_прежнюю_страницу(client, client_a):
    client.force_login(client_a.user)

    response = client.get(reverse("storage_units:logout"), HTTP_REFERER="/faq/")

    assert response.url == "/faq/"


def test_выход_из_кабинета_ведёт_на_главную(client, client_a):
    client.force_login(client_a.user)

    response = client.get(reverse("storage_units:logout"), HTTP_REFERER="/my-rent/")

    assert response.url == "/"
