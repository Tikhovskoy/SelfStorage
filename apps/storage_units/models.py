from django.core.validators import MinValueValidator
from django.db import models


class Warehouse(models.Model):
	ADVANTAGE_CHOICE = {
		('metro', 'Рядом с метро'),
		('parking', 'Парковка'),
		('ceilings', 'Высокие потолки'),
		('box', 'Большие боксы')
	}

	name = models.CharField(max_length=100, verbose_name='Название склада')
	address = models.TextField(verbose_name='Адрес')
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
	square = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], verbose_name='Площадь')
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

	class Meta:
		verbose_name = 'Бокс'
		verbose_name_plural = 'Боксы'

	def __str__(self):
		return f'№ бокса {self.id}'
