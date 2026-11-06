from datetime import date, timedelta

from django.urls import reverse

from apps.storage_units.models import Rental

NEW_END = (date.today() + timedelta(days=60)).isoformat()


def _renew_url(box):
    return reverse("storage_units:renew_box", args=[box.id])


def test_чужой_пользователь_не_может_продлить_аренду(
    client, client_a, client_b, make_rental
):
    rental = make_rental(client_a)
    old_end = rental.end_date
    client.force_login(client_b.user)

    response = client.post(_renew_url(rental.box), {"renew_date": NEW_END})

    assert response.status_code == 404
    rental.refresh_from_db()
    rental.box.refresh_from_db()
    assert rental.end_date == old_end
    assert rental.client == client_a
    assert rental.box.paid_for == old_end
    assert rental.box.tenant == client_a


def test_свободный_бокс_нельзя_взять_через_продление(client, client_a, make_box):
    box = make_box()
    client.force_login(client_a.user)

    response = client.post(_renew_url(box), {"renew_date": NEW_END})

    assert response.status_code == 404
    box.refresh_from_db()
    assert box.tenant is None
    assert box.is_free
    assert not Rental.objects.filter(box=box).exists()


def test_арендатор_продлевает_свой_бокс(client, client_a, make_rental):
    rental = make_rental(client_a)
    client.force_login(client_a.user)

    response = client.post(_renew_url(rental.box), {"renew_date": NEW_END})

    assert response.status_code == 302
    rental.refresh_from_db()
    rental.box.refresh_from_db()
    assert rental.end_date.isoformat() == NEW_END
    assert rental.box.paid_for.isoformat() == NEW_END


def test_аноним_отправляется_на_вход(client, client_a, make_rental):
    rental = make_rental(client_a)

    response = client.post(_renew_url(rental.box), {"renew_date": NEW_END})

    assert response.status_code == 302
    assert response.url.startswith("/login/")


def test_продление_только_методом_post(client, client_a, make_rental):
    rental = make_rental(client_a)
    client.force_login(client_a.user)

    assert client.get(_renew_url(rental.box)).status_code == 405
