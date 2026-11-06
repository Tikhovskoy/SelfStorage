import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    "url_name",
    ["index", "boxes_list", "faq", "tariffs", "privacy_policy"],
)
def test_публичные_страницы_открываются(client, db, url_name):
    response = client.get(reverse(f"storage_units:{url_name}"))

    assert response.status_code == 200


def test_личный_кабинет_требует_входа(client, db):
    response = client.get(reverse("storage_units:my_rent"))

    assert response.status_code == 302
    assert response.url.startswith("/login/")
