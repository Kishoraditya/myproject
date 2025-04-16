"""
Browser-like integration tests for home app.
These tests simulate browser interaction without requiring Selenium.
"""
import json

import pytest
from django.test import Client
from django.urls import reverse

from home.models import LandingPage

# Apply the django_db marker to allow database access
pytestmark = pytest.mark.django_db


class TestBrowserIntegration:
    """Tests that simulate browser-like interactions."""

    @pytest.fixture(autouse=True)
    def setup(self, client, home_page, site, admin_user, default_locale):
        """Set up test environment before each test."""
        self.client = client
        self.home_page = home_page
        self.site = site
        self.admin_user = admin_user
        self.admin_client = Client()
        self.admin_client.force_login(admin_user)
        self.default_locale = default_locale

        # Create a test landing page with form elements
        self.landing_page = LandingPage(
            title="Form Test Page",
            slug="form-test-page",
            hero_title="Test Form Page",
            hero_subtitle="Test using forms",
            hero_cta_text="Submit",
            hero_cta_link="https://example.com/form",
            body=json.dumps(
                [
                    {"type": "heading", "value": "Test Form", "id": "1"},
                    {
                        "type": "paragraph",
                        "value": "<p>Please submit the form below</p>",
                        "id": "2",
                    },
                ]
            ),
            locale=self.default_locale,
        )

        # Add required fields
        if hasattr(self.landing_page, "schema_org_type"):
            self.landing_page.schema_org_type = "WebPage"

        # Add the page to the home page
        self.home_page.add_child(instance=self.landing_page)
        self.landing_page.save_revision().publish()

    def test_form_submission_flow(self):
        """Test a complete form submission flow."""
        # First visit the landing page with the form
        response = self.client.get(self.landing_page.url)
        assert response.status_code == 200

        # Extract the search form action URL (in a real test, we'd parse the HTML)
        search_url = reverse("search")

        # Submit the search form with GET instead of POST
        form_data = {"query": "test search query"}
        response = self.client.get(search_url, form_data)

        # Check behavior - no redirection needed for GET
        assert response.status_code == 200
        assert "test search query" in response.context.get("search_query", "")

    def test_admin_navigation_flow(self):
        """Test navigation flow in the admin interface."""
        # Skip if not logged in as admin
        if not self.admin_user:
            pytest.skip("No admin user available")

        # Access the admin interface
        response = self.admin_client.get("/admin/")
        assert response.status_code == 200

        # Navigate to pages area
        response = self.admin_client.get("/admin/pages/")
        assert response.status_code == 200

        # Navigate to a specific page for editing
        edit_url = f"/admin/pages/{self.landing_page.id}/edit/"
        response = self.admin_client.get(edit_url)
        assert response.status_code == 200

        # Check the presence of form fields in the edit page
        content = response.content.decode("utf-8")
        assert "title" in content
        assert "hero_title" in content

    def test_page_navigation_breadcrumb_flow(self):
        """Test user navigation through breadcrumbs."""
        # Create a hierarchy of pages for breadcrumb navigation
        parent_page = LandingPage(
            title="Parent Page",
            slug="parent-page",
            hero_title="Parent Page Title",
            hero_cta_link="https://example.com",
            body=json.dumps(
                [{"type": "paragraph", "value": "<p>Parent content</p>", "id": "1"}]
            ),
            schema_org_type="WebPage",
            locale=self.default_locale,
        )

        self.home_page.add_child(instance=parent_page)
        parent_page.save_revision().publish()

        child_page = LandingPage(
            title="Child Page",
            slug="child-page",
            hero_title="Child Page Title",
            hero_cta_link="https://example.com",
            body=json.dumps(
                [{"type": "paragraph", "value": "<p>Child content</p>", "id": "1"}]
            ),
            schema_org_type="WebPage",
            locale=self.default_locale,
        )

        parent_page.add_child(instance=child_page)
        child_page.save_revision().publish()

        # Visit the child page
        response = self.client.get("/parent-page/child-page/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Check breadcrumb content (we'd parse HTML in a real test)
        assert "Home" in content
        assert "Parent Page" in content
        assert "Child Page" in content

        # Navigate up through breadcrumb to parent
        response = self.client.get("/parent-page/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Parent Page Title" in content

        # Navigate to home
        response = self.client.get("/")
        assert response.status_code == 200
