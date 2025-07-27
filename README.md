# SelfStorage

Онлайн-сервис для аренды складских боксов.

---

## Назначение проекта

Проект создан для проверки спроса на услуги хранения вещей. Позволяет клиентам:

* Освободить домашнее пространство от сезонных и редко используемых вещей.
* Сохранить вещи на время переезда.
* Хранить крупные предметы.

---

## Основной функционал

* Регистрация и авторизация пользователей (email, пароль).
* Личный кабинет с возможностью редактирования профиля и просмотра списка вещей.
* Оформление аренды боксов с выбором склада и условий хранения.
* Применение промокодов для получения скидок.
* Управление складами, клиентами и заказами через Django admin.

---

## Технический стек

* Django
* PostgreSQL
* Docker, Docker Compose
* Bootstrap 5
* JavaScript

---

## Быстрый старт (локально)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Tikhovskoy/SelfStorage.git
cd SelfStorage

# 2. Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Создай .env файл по примеру ниже

# 5. Примени миграции и собери статику
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Запусти сервер
python manage.py runserver
```

---

## Деплой на сервер (Docker)

Убедись, что на сервере установлен Docker и Docker Compose:

```bash
# 1. Склонируй репозиторий на сервер
git clone https://github.com/Tikhovskoy/SelfStorage.git
cd SelfStorage

# 2. Создай .env файл рядом с docker-compose.yml

# 3. Запусти скрипт деплоя
bash scripts/deploy.sh
```

Контейнеры запускаются с флагом `--restart unless-stopped`, что гарантирует автоматический перезапуск после сбоев или перезагрузки сервера.

---

## Пример .env файла

```env
DEBUG=False
SECRET_KEY=django-insecure-ваш_секретный_ключ
ALLOWED_HOSTS=127.0.0.1,localhost

USE_SQLITE=False

POSTGRES_DB=ваше_название_базы
POSTGRES_USER=ваше_имя_пользователя
POSTGRES_PASSWORD=ваш_пароль
POSTGRES_HOST=ваш_хост
POSTGRES_PORT=5432
```

---

## Структура проекта

```
selfstorage/
├── apps/                     # Приложения проекта
│   ├── orders/               # Заказы и аренда
│   ├── customers/            # Пользователи и профили
│   ├── storage_units/        # Склады и боксы
│   ├── promo/                # Промокоды и акции
│   └── business/             # Услуги для юрлиц
├── docker/                   # Конфигурации Docker (backend, nginx)
├── selfstorage/              # Конфигурация Django (settings, urls)
├── templates/                # HTML-шаблоны (Bootstrap 5)
├── static/                   # Статика (CSS, JS, изображения)
├── staticfiles/              # Собранная статика
├── media/                    # Пользовательские файлы
├── scripts/                  # Скрипты деплоя
├── docker-compose.yml
├── deploy.sh
├── deploy-remote.sh
├── requirements.txt
├── manage.py
└── README.md
```

---

## Доступ к Django Admin

После запуска контейнеров создай суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

Панель администратора доступна по адресу:
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Доступ к сайту

[http://158.160.80.113/](SelfStorage)

