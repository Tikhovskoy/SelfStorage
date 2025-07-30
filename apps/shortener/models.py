import uuid

from django.db import models


class ShortLink(models.Model):
    token = models.CharField(
        max_length=12, unique=True, editable=False, verbose_name="Токен"
    )
    target_url = models.URLField(verbose_name="Целевая ссылка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    click_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество переходов"
    )

    class Meta:
        verbose_name = "Короткая ссылка"
        verbose_name_plural = "Короткие ссылки"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.token} → {self.target_url}"
