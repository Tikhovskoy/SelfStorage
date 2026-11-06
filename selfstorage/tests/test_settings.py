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
