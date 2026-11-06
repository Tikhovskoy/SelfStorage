from django.core.checks import run_checks
from django.test.utils import override_settings

from selfstorage.tests.settings_loader import load_settings


def test_статика_сайта_собирается_и_при_выключенном_debug(monkeypatch):
    settings = load_settings(monkeypatch, DEBUG="False")

    assert settings.BASE_DIR / "static" in settings.STATICFILES_DIRS
    assert settings.STATIC_ROOT == settings.BASE_DIR / "staticfiles"


def test_debug_выключен_по_умолчанию(monkeypatch):
    settings = load_settings(monkeypatch)

    assert settings.DEBUG is False


def test_debug_включается_только_через_окружение(monkeypatch):
    settings = load_settings(monkeypatch, DEBUG="True")

    assert settings.DEBUG is True


def _deploy_check_ids(settings_module):
    """Идентификаторы замечаний check --deploy для заданных настроек."""
    names = ["DEBUG", "SECRET_KEY", "ALLOWED_HOSTS"] + [
        name
        for name in dir(settings_module)
        if name.startswith(("SECURE_", "SESSION_COOKIE_", "CSRF_COOKIE_"))
    ]
    values = {name: getattr(settings_module, name) for name in names}
    with override_settings(**values):
        return {message.id for message in run_checks(include_deployment_checks=True)}


def test_боевые_настройки_по_https_проходят_check_deploy(monkeypatch):
    settings = load_settings(
        monkeypatch,
        ALLOWED_HOSTS="selfstorage.example",
        USE_HTTPS="True",
        SECURE_HSTS_INCLUDE_SUBDOMAINS="True",
        SECURE_HSTS_PRELOAD="True",
    )

    assert _deploy_check_ids(settings) == set()


def test_по_https_включены_защищённые_куки_и_редирект(monkeypatch):
    settings = load_settings(monkeypatch, USE_HTTPS="True")

    assert settings.SECURE_SSL_REDIRECT is True
    assert settings.SESSION_COOKIE_SECURE is True
    assert settings.CSRF_COOKIE_SECURE is True
    assert settings.SECURE_HSTS_SECONDS > 0
    assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")


def test_по_http_защищённые_куки_и_редирект_выключены(monkeypatch):
    settings = load_settings(monkeypatch)

    assert settings.SECURE_SSL_REDIRECT is False
    assert settings.SESSION_COOKIE_SECURE is False
    assert not hasattr(settings, "SECURE_PROXY_SSL_HEADER")


def test_по_http_остаются_только_замечания_про_https(monkeypatch):
    settings = load_settings(monkeypatch)

    # W004 HSTS, W008 редирект, W012 и W016 защищённые куки — недоступны без https
    assert _deploy_check_ids(settings) == {
        "security.W004",
        "security.W008",
        "security.W012",
        "security.W016",
    }
