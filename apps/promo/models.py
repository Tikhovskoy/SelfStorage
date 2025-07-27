from django.db import models
from django.utils import timezone
from apps.orders.models import Client


class PromoCode(models.Model):
    code = models.CharField("Промокод", max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField("Скидка (%)")
    active_from = models.DateField("Действует с")
    active_to = models.DateField("Действует до")
    usage_limit = models.PositiveIntegerField("Лимит использований", null=True, blank=True)
    used_count = models.PositiveIntegerField("Количество использований", default=0)
    one_time_per_user = models.BooleanField("Ограничить 1 раз на клиента", default=False)
    used_clients = models.ManyToManyField(Client, blank=True, related_name="used_promo_codes", verbose_name="Клиенты, использовавшие промокод")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ["-active_to"]

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    def is_active(self, client=None):
        today = timezone.now().date()

        if not (self.active_from <= today <= self.active_to):
            return False

        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False

        if self.one_time_per_user and client is not None and self.used_clients.filter(pk=client.pk).exists():
            return False

        return True
