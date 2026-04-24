import django
from django.conf import settings


def pytest_configure(config):
    settings.DATABASES["default"].setdefault("TEST", {})