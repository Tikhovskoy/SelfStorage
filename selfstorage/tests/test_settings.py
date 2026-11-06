from selfstorage.tests.settings_loader import load_settings


def test_статика_сайта_собирается_и_при_выключенном_debug(monkeypatch):
    settings = load_settings(monkeypatch, DEBUG="False")

    assert settings.BASE_DIR / "static" in settings.STATICFILES_DIRS
    assert settings.STATIC_ROOT == settings.BASE_DIR / "staticfiles"
