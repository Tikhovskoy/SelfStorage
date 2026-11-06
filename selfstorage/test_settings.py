"""Настройки для тестов.

Не зависят от локального .env: ключ подставляется по умолчанию,
база — SQLite в памяти, пароли хешируются быстрым алгоритмом.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from selfstorage.settings import *  # noqa: E402,F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
