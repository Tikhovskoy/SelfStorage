import re

import pytest
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

NEW_PASSWORD = "Brand-New-Pass-98765"


def _link_from_email(message):
    match = re.search(r"https?://[^/\s]+(/password-reset/\S+)", message.body)
    assert match, message.body
    return match.group(1)


def _without_csrf(response):
    html = response.content.decode()
    return re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", html)


@pytest.fixture
def user(client_a):
    return client_a.user


def test_старый_эндпоинт_сброса_без_подтверждения_удалён(client, user, password):
    response = client.post(
        "/simple-reset/",
        {
            "email": user.email,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 404
    user.refresh_from_db()
    assert user.check_password(password)


@pytest.mark.parametrize("token", ["set-password", "bad-token", "abc-123456"])
def test_пароль_нельзя_сменить_без_токена_из_письма(client, user, password, token):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = reverse("orders:password_reset_confirm", args=[uid, token])

    client.post(url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})

    user.refresh_from_db()
    assert user.check_password(password)
    assert not user.check_password(NEW_PASSWORD)


def test_запрос_сброса_отправляет_письмо_со_ссылкой(client, user):
    response = client.post(reverse("orders:password_reset"), {"email": user.email})

    assert response.status_code == 302
    assert response.url == reverse("orders:password_reset_done")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]
    assert _link_from_email(mail.outbox[0])


def test_ссылка_из_письма_меняет_пароль(client, user, password):
    client.post(reverse("orders:password_reset"), {"email": user.email})
    link = _link_from_email(mail.outbox[0])

    response = client.get(link, follow=True)
    assert response.status_code == 200
    set_password_url = response.redirect_chain[-1][0]

    response = client.post(
        set_password_url,
        {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:password_reset_complete")
    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)
    assert not user.check_password(password)
    assert client.login(username=user.username, password=NEW_PASSWORD)


def test_ссылка_из_письма_работает_один_раз(client, user):
    client.post(reverse("orders:password_reset"), {"email": user.email})
    link = _link_from_email(mail.outbox[0])
    response = client.get(link, follow=True)
    client.post(
        response.redirect_chain[-1][0],
        {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )

    repeat = client.get(link)

    assert repeat.context["validlink"] is False


def test_слабый_пароль_отклоняется_и_не_сохраняется(client, user, password):
    client.post(reverse("orders:password_reset"), {"email": user.email})
    response = client.get(_link_from_email(mail.outbox[0]), follow=True)

    response = client.post(
        response.redirect_chain[-1][0],
        {"new_password1": "12345678", "new_password2": "12345678"},
    )

    assert response.status_code == 200
    assert response.context["form"].errors
    user.refresh_from_db()
    assert user.check_password(password)


def test_ответ_не_раскрывает_наличие_email(client, user):
    url = reverse("orders:password_reset")

    known = client.post(url, {"email": user.email}, follow=True)
    unknown = client.post(url, {"email": "nobody@example.com"}, follow=True)

    assert known.redirect_chain == unknown.redirect_chain
    assert known.status_code == unknown.status_code == 200
    assert _without_csrf(known) == _without_csrf(unknown)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]


def test_в_форме_входа_есть_ссылка_на_восстановление_пароля(client, db):
    response = client.get(reverse("storage_units:index"))

    assert reverse("orders:password_reset") in response.content.decode()
