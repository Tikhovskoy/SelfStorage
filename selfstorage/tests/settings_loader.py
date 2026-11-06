import importlib.util
from pathlib import Path

import environ

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.py"


def load_settings(monkeypatch, **env_vars):
    """Загружает selfstorage/settings.py заново при заданных переменных окружения.

    Модуль подгружается отдельным объектом и не трогает уже настроенный
    django.conf.settings. Чтение локального .env отключено, чтобы результат
    не зависел от файла на машине разработчика.
    """
    monkeypatch.setattr(environ.Env, "read_env", classmethod(lambda cls, *a, **k: None))
    for name in ("DEBUG", "USE_SQLITE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("SECRET_KEY", "x" * 60)
    for name, value in env_vars.items():
        monkeypatch.setenv(name, value)

    spec = importlib.util.spec_from_file_location("settings_under_test", SETTINGS_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
