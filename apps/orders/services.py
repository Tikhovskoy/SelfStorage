from apps.orders.models import Client


def ensure_client(user):
    """Возвращает профиль клиента пользователя, создавая его при отсутствии.

    Нужен для аккаунтов без профиля (например, созданных через createsuperuser
    или до появления сигнала), чтобы view не падали с Client.DoesNotExist.
    """
    client, _ = Client.objects.get_or_create(
        user=user,
        defaults={
            "first_name": user.first_name or user.username,
            "last_name": user.last_name,
            "email": user.email,
        },
    )
    return client
