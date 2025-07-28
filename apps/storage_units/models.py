from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Min, Q
from .qr_utils import generate_qr_code_image
import uuid

from apps.orders.models import Client


class Warehouse(models.Model):
	ADVANTAGE_CHOICE = {
		('metro', 'Рядом с метро'),
		('parking', 'Парковка'),
		('ceilings', 'Высокие потолки'),
		('box', 'Большие боксы'),
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

	@property
	def min_tariff_price(self):
		min_price = self.boxes.aggregate(Min('price'))['price__min']

		if min_price is None:
			return None

		return min_price

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
		help_text='Не обязятельно к заполнению. Расчитывается автоматически'
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

class Rental(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    box = models.OneToOneField(Box, on_delete=models.CASCADE, verbose_name='Бокс')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    qr_token = models.CharField(max_length=64, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex
        if not self.qr_code:
            url = f"https://your-domain.ru/open-box/?token={self.qr_token}"
            self.qr_code = generate_qr_code_image(url, filename=f"qr_{self.qr_token}.png")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Аренда бокса {self.box.id} клиентом {self.client.user.username}"

    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"