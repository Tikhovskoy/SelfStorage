# SelfStorage

Онлайн-сервис для аренды складских боксов. Командный учебный проект.

---

## Назначение проекта

Проект создан для проверки спроса на услуги хранения вещей. Позволяет клиентам:

* Освободить домашнее пространство от сезонных и редко используемых вещей.
* Сохранить вещи на время переезда.
* Хранить крупные предметы.

---

## Основной функционал

* Регистрация и авторизация пользователей (email, пароль).
* Восстановление пароля по одноразовой ссылке из письма.
* Личный кабинет: редактирование профиля (email, телефон, фото, пароль) и список арендованных боксов с продлением аренды.
* Аренда бокса на выбранный срок на странице «Арендовать бокс».
* Промокоды: скидка на аренду и продление.
* QR-код для каждой аренды (заготовка: ссылка в коде пока ведёт на заглушечный адрес, страницы открытия бокса нет).
* Тарифы, заявка на расчёт стоимости (заглушка: письмо клиенту не отправляется, заявка попадает в админку).
* Управление складами, боксами, клиентами, арендами, тарифами, промокодами и короткими ссылками через Django admin.

---

## Технический стек

* Python 3.12, Django 5.2
* PostgreSQL (SQLite для локальной разработки)
* Docker, Docker Compose, nginx, gunicorn
* Bootstrap 5, JavaScript
* pytest, flake8, bandit, GitHub Actions

---

## Быстрый старт (локально)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Tikhovskoy/SelfStorage.git
cd SelfStorage

# 2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Установи зависимости (для запуска сайта достаточно requirements.txt)
pip install -r requirements-dev.txt

# 4. Создай .env из примера и при желании поправь значения
cp .env.example .env

# 5. Примени миграции и создай администратора
python manage.py migrate
python manage.py createsuperuser

# 6. Запусти сервер
python manage.py runserver
```

Сайт откроется на http://127.0.0.1:8000/, админка — на `/admin/`.

В `.env.example` включён `DEBUG=True`: без него (по умолчанию `DEBUG=False`) сервер разработки не отдаёт статику. Письма восстановления пароля при `EMAIL_BACKEND=...console.EmailBackend` печатаются в консоль, где запущен сервер.

Демонстрационные боксы для уже созданного склада: `python manage.py creation_boxes`.

---

## Запуск через Docker Compose

В Compose три сервиса: `db` (PostgreSQL 14), `backend` (gunicorn) и `nginx` (порт 80, раздаёт статику и медиа).

```bash
# 1. Создай .env рядом с docker-compose.yml
cp .env.example .env
```

Отредактируй `.env` для Docker:

```env
DEBUG=False
SECRET_KEY=<длинная случайная строка>
ALLOWED_HOSTS=localhost,127.0.0.1
USE_SQLITE=False
POSTGRES_DB=selfstorage
POSTGRES_USER=selfuser
POSTGRES_PASSWORD=<свой пароль>
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Контейнер базы читает `POSTGRES_*` из того же `.env`, поэтому пароль задаётся в одном месте.

```bash
# 2. Собери и запусти контейнеры
docker compose up -d --build

# 3. Примени миграции, собери статику и создай администратора
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py collectstatic --noinput
docker compose exec backend python manage.py createsuperuser
```

Сайт доступен на http://localhost/, админка — на http://localhost/admin/. Шаги 2–3 (кроме `createsuperuser`) выполняет скрипт `deploy.sh`.

---

## Деплой на сервер

Нужны Docker и Docker Compose. Сервер и первый запуск настраиваются так же, как в разделе выше (`.env` лежит на сервере и в репозиторий не попадает).

```bash
# На сервере: подтянуть код, пересобрать контейнеры, применить миграции, собрать статику
./deploy.sh

# С локальной машины: скопировать проект по rsync и запустить deploy.sh на сервере
./deploy-remote.sh
```

Скрипт `deploy-remote.sh` использует SSH-хост `selfstorage` из `~/.ssh/config` и каталог `/home/ubuntu/selfstorage`.

Миграции хранятся в репозитории, на сервере выполняется только `migrate`. **Не запускай `makemigrations` на сервере.**

### HTTPS

Когда сайт открывается по https (TLS настраивается на nginx), добавь в `.env` `USE_HTTPS=True`: включатся редирект на https, защищённые куки и HSTS. По обычному http флаг должен оставаться выключенным, иначе вход на сайте перестанет работать.

### Однократный переход существующего сервера на хранимые миграции

Раньше миграции создавались прямо на сервере и в git не попадали. Чтобы перейти на миграции из репозитория:

```bash
# 1. Резервная копия базы
docker compose exec db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup-$(date +%F).sql

# 2. Удали миграции, созданные на сервере раньше (их заменят файлы из репозитория)
find apps -path '*/migrations/0*.py' -delete

# 3. Задеплой новую версию
./deploy-remote.sh

# 4. Проверь, что схема совпадает с кодом (ожидается «No changes detected»)
docker compose exec backend python manage.py makemigrations --check --dry-run
```

Если в базе уже записаны миграции `0001_initial`, деплой применит только новые (`migrate`). Если история миграций потеряна (таблицы есть, а записей в `django_migrations` нет) и `migrate` падает с ошибкой «relation ... already exists», выполни: `docker compose exec backend python manage.py migrate --fake-initial`.

---

## Переменные окружения

Полный список с пояснениями — в [.env.example](.env.example). Главное:

| Переменная | Назначение |
| --- | --- |
| `DEBUG` | Режим отладки, по умолчанию выключен |
| `SECRET_KEY` | Секретный ключ Django, обязателен |
| `ALLOWED_HOSTS` | Разрешённые хосты через запятую |
| `USE_SQLITE`, `POSTGRES_*` | Выбор и параметры базы данных |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | Отправка писем (по умолчанию — вывод в консоль) |
| `USE_HTTPS` | Редирект на https, защищённые куки, HSTS |
| `SELFSTORAGE_DOMAIN` | Адрес сайта для QR-кодов и коротких ссылок |

---

## Тесты и проверки качества

```bash
pytest --cov                              # тесты и покрытие apps/orders, apps/storage_units, apps/promo (порог 70%)
flake8                                    # линтер, настройки в .flake8
bandit -q -r apps selfstorage -c .bandit  # проверка безопасности
python manage.py makemigrations --check --dry-run   # модели совпадают с миграциями
```

Тесты используют отдельные настройки `selfstorage/test_settings.py` (SQLite в памяти) и не требуют `.env`. Те же проверки, а также применение миграций на PostgreSQL и `check --deploy` запускаются в GitHub Actions (`.github/workflows/ci.yml`) на каждый pull request и на push в `main`.

---

## Структура проекта

```
selfstorage/
├── apps/                     # Приложения проекта
│   ├── orders/               # Клиенты, профиль, регистрация, вход, восстановление пароля
│   ├── storage_units/        # Склады, боксы, тарифы, аренды, личный кабинет
│   ├── promo/                # Промокоды и сервис их применения
│   └── shortener/            # Короткие ссылки
├── docker/                   # Конфигурации Docker (backend, nginx)
├── selfstorage/              # Конфигурация Django (settings, urls) и тесты настроек
├── templates/                # HTML-шаблоны (Bootstrap 5)
├── static/                   # Статика (CSS, JS, изображения)
├── .github/workflows/        # CI
├── docker-compose.yml
├── deploy.sh                 # Деплой на сервере
├── deploy-remote.sh          # Деплой с локальной машины
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── manage.py
└── README.md
```

Каталоги `staticfiles/` и `media/` создаются при работе и в репозиторий не входят.

---

## Доступ к Django Admin

После запуска контейнеров создай суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

Панель администратора доступна по адресу:
[http://158.160.80.113/admin/](http://158.160.80.113/admin/)

## Доступ к сайту

[SelfStorage](http://158.160.80.113/)
