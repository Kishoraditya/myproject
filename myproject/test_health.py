"""
Tests for health check endpoint.
"""
from unittest.mock import patch

import pytest
from django.db.utils import OperationalError
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_health_check_with_db(client):
    """Test health check when database is available."""
    url = reverse("health_check")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db_status"] == "ok"


@patch("myproject.health.connections")
def test_health_check_without_db(mock_connections, client):
    """Test health check when database is not available."""
    # Mock the database connection to raise an OperationalError
    mock_cursor = mock_connections.__getitem__.return_value.cursor
    mock_cursor.side_effect = OperationalError("Connection refused")

    url = reverse("health_check")
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db_status"] == "not_available"


def test_health_check_post_method(client):
    """Test health check with POST method (CSRF exempt)."""
    url = reverse("health_check")
    response = client.post(url)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
