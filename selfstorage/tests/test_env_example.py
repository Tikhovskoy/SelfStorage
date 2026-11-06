import re

from selfstorage.tests.settings_loader import SETTINGS_FILE, load_settings

ENV_EXAMPLE = SETTINGS_FILE.parent.parent / ".env.example"


def _example_values():
    values = {}
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            name, _, value = line.partition("=")
            values[name.strip()] = value.strip()
    return values


def test_в_примере_описаны_все_переменные_окружения_из_настроек():
    used = set(
        re.findall(r'env(?:\.\w+)?\(\s*"([A-Z_]+)"', SETTINGS_FILE.read_text("utf-8"))
    )
    documented = set(
        re.findall(r"^#?\s*([A-Z_]+)=", ENV_EXAMPLE.read_text("utf-8"), re.M)
    )

    assert used - documented == set()


def test_пример_окружения_загружается_настройками(monkeypatch):
    settings = load_settings(monkeypatch, **_example_values())

    assert settings.DEBUG is True
    assert settings.USE_SQLITE is True
    assert settings.EMAIL_BACKEND.endswith("console.EmailBackend")
    assert settings.SECURE_SSL_REDIRECT is False
