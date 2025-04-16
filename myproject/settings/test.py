"""
Test settings configuration - extends dev settings but disables migrations
"""
import os  # Add explicit import

from django.db import connection  # Move import to top

from .dev import *  # noqa

# Use in-memory SQLite database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable migrations by replacing the migration module with a dummy one
# This significantly speeds up tests


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Remove any conflicting storage settings
if "STATICFILES_STORAGE" in locals():
    del STATICFILES_STORAGE

if "STORAGES" in locals():
    del STORAGES

# Set up test file storage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_ROOT = os.path.join(BASE_DIR, "test-media")  # noqa
STATIC_ROOT = os.path.join(BASE_DIR, "test-static")  # noqa


def setup_sqlite_fts():
    """Setup SQLite FTS tables after database creation."""
    if connection.vendor == "sqlite":
        with connection.cursor() as cursor:
            # Create FTS tables manually
            cursor.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS wagtailsearch_indexentry_fts "
                'USING FTS5(autocomplete, title, body, content="wagtailsearch_indexentry")'
            )


# Call this when DB is ready
setup_sqlite_fts()
