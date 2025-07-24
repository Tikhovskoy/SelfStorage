from django.core.validators import MinValueValidator
from django.db import models

from apps.orders.models import Client


class Warehouse(models.Model):
	ADVANTAGE_CHOICE = {
		('metro', 'Рядом с метро'),
		('parking', 'Парковка'),
		('ceilings', 'Высокие потолки'),
		('box', 'Большие боксы')
	}

	name = models.CharField(max_length=100, verbose_name='Название склада')
	address = models.TextField(verbose_name='Адрес')
	image = models.ImageField(
		null=True,
		blank=True,
		verbose_name='Фото склада',
	)
	temperature = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		null=True,
		blank=True,
		verbose_name='Температура на складе',
	)
	ceilings = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		verbose_name='Высота потолка',
	)
	advantage = models.CharField(
		choices=ADVANTAGE_CHOICE,
		max_length=100,
		null=True,
		blank=True,
		verbose_name='Преимущество склада',
	)

	is_default_nearest = models.BooleanField(
		default=False,
		verbose_name='Ближайший склад по умолчанию'
	)

	class Meta:
		verbose_name = 'Склад'
		verbose_name_plural = 'Склады'

	def __str__(self):
		return f'Склад {self.name}'


class Box(models.Model):
	warehouse = models.ForeignKey(
		Warehouse,
		on_delete=models.CASCADE,
		related_name='boxes',
		verbose_name='Склад',
	)
	floor = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Этаж')
	length = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Длина')
	width = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Ширина')
	height = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		validators=[MinValueValidator(1)],
		verbose_name='Высота',
	)
	square = models.PositiveSmallIntegerField(
		null=True,
		blank=True,
		validators=[MinValueValidator(1)],
		verbose_name='Площадь',
	)
	price = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		verbose_name='Цена аренды',
	)
	is_free = models.BooleanField(
		default=True,
		null=True,
		blank=True,
		verbose_name='Бокс свободен',
	)
	tenant = models.ForeignKey(
		Client,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='rent_boxes',
		verbose_name='Арендатор',
	)
	paid_for = models.DateField(
		null=True,
		blank=True,
		verbose_name='Оплачен до',
	)

	def save(self, *args, **kwargs):
		self.square = self.length * self.width
		super().save(*args, **kwargs)

	class Meta:
		verbose_name = 'Бокс'
		verbose_name_plural = 'Боксы'

	def __str__(self):
		return f'№ бокса {self.id}'


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена в месяц (руб.)")
    min_square_meters = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Минимальная площадь бокса (м²)"
    )
    max_square_meters = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
        verbose_name="Максимальная площадь бокса (м²)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Подробное описание тарифа"
    )

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ['min_square_meters', 'price']

    def __str__(self):
        return f"{self.name} - {self.price} ₽/мес ({self.min_square_meters}-{self.max_square_meters if self.max_square_meters else '∞'} м²)"
