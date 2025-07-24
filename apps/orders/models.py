from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		related_name='client_profile',
		null=True,
		blank=True,
		verbose_name='Пользователь',
	)
	first_name = models.CharField(
		max_length=100,
		verbose_name='Имя',
	)
	last_name = models.CharField(
		max_length=100,
		null=True,
		blank=True,
		verbose_name='Фамилия',
	)
	image = models.ImageField(
		null=True,
		blank=True,
		verbose_name='Фото клиента',
	)
	email = models.EmailField(
		max_length=200,
		null=True,
		blank=True,
		verbose_name='Email',
	)
	phone = PhoneNumberField(
		region='RU',
		null=True,
		blank=True,
		verbose_name='Телефон',
	)
	registered_at = models.DateField(
		auto_now=True,
		verbose_name='Дата регистрации',
	)

	class Meta:
		verbose_name = 'Клиента'
		verbose_name_plural = 'Клиенты'

	def __str__(self):
		if self.last_name:
			return f'{self.first_name} {self.last_name}'
		return self.first_name
