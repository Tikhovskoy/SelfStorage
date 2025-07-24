from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Client


class RegistrationForm(forms.Form):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=False)
    email = forms.EmailField(label='E-mail', max_length=254)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают')

        if User.objects.filter(username=cleaned_data.get('email')).exists():
            self.add_error('email', 'Пользователь с таким email уже зарегистрирован')

        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data.get('last_name', ''),
        )
        Client.objects.create(
            user=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data.get('last_name', ''),
            email=email,
        )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email / Username")
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'phone', 'image']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control fs_24 ps-2 SelfStorage__input',
                'id': 'EMAIL',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control fs_24 ps-2 SelfStorage__input',
                'id': 'PHONE',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control fs_24 ps-2 SelfStorage__input',
                'id': 'IMAGE',
            }),
        }