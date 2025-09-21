from .settings import *
import importlib, sys

# Swap real app with mock app (same app_label)
MOCK_APPS = {"notification": "tests.mocks.notification"}

def _swap_apps(installed):
    return [MOCK_APPS.get(app.split(".")[0], app) for app in installed]

INSTALLED_APPS = _swap_apps(INSTALLED_APPS)

# Alias specific modules to ensure they resolve to mocks
# Only alias modules that don't cause AppRegistryNotReady errors
try:
    sys.modules["notification.urls"] = importlib.import_module("tests.mocks.notification.urls")
except ModuleNotFoundError:
    pass

# This will make Django load the mock app's models when notification.models is imported
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MIGRATION_MODULES = {app.split(".")[0]: None for app in INSTALLED_APPS}
DISABLE_SIGNAL_EMISSION = True
DEBUG = False