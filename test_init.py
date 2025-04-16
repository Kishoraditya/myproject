"""
Simple test to verify that Django is properly initialized.
"""

import django


def test_django_initialization():
    """Test that Django is properly initialized."""
    # This test should pass if Django is properly initialized
    assert django.apps.apps.ready
    assert django.apps.apps.get_app_config("home") is not None
    assert django.apps.apps.get_app_config("search") is not None
