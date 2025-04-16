"""
Tests for home app views.
"""
import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from wagtail import hooks
from wagtail.models import Locale, Page
from wagtail.test.utils.page_tests import WagtailPageTestCase

from home.models import HomePage, LandingPage

# Apply the django_db marker to allow database access
pytestmark = pytest.mark.django_db


@pytest.mark.views
def test_homepage_200(client, home_page, site):
    """Test homepage returns 200 status code."""
    # Get the homepage URL
    response = client.get("/")

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Verify it's using the right template
    assert "home/home_page.html" in [t.name for t in response.templates]


@pytest.mark.views
def test_homepage_content(client, home_page, site):
    """Test homepage renders with expected content."""
    # Test that the homepage contains expected content
    response = client.get("/")

    # Check for page title in the content
    assert home_page.title in response.content.decode("utf-8")

    # Check for hero section content
    if hasattr(home_page, "hero_title") and home_page.hero_title:
        assert home_page.hero_title in response.content.decode("utf-8")

    if hasattr(home_page, "hero_subtitle") and home_page.hero_subtitle:
        assert home_page.hero_subtitle in response.content.decode("utf-8")


@pytest.mark.views
def test_landing_page_200(client, home_page, landing_page, site):
    """Test landing page returns 200 status code."""
    # Get the landing page URL
    response = client.get(landing_page.url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Verify it's using the right template
    assert "home/landing_page.html" in [t.name for t in response.templates]


@pytest.mark.views
def test_landing_page_content(client, home_page, landing_page, site):
    """Test landing page renders with expected content."""
    # Test that the landing page contains expected content
    response = client.get(landing_page.url)

    # Check for page title in the content
    assert landing_page.title in response.content.decode("utf-8")

    # Check for hero section content if applicable
    if hasattr(landing_page, "hero_title") and landing_page.hero_title:
        assert landing_page.hero_title in response.content.decode("utf-8")


@pytest.mark.views
def test_404_page(client, site):
    """Test 404 page behavior."""
    # Request a page that doesn't exist
    response = client.get("/this-page-does-not-exist/")

    # Check that the response is 404
    assert response.status_code == 404

    # Verify it's using the 404 template
    assert "404.html" in [t.name for t in response.templates]


@pytest.mark.skip(reason="Admin tests require more complex setup with Wagtail admin")
class TestAdminPages(WagtailPageTestCase):
    """Tests for admin pages requiring authentication."""

    def setUp(self):
        # WagtailTestCase setUp handles basic setup
        super().setUp()

        # Get existing pages from the test database
        # These should have been created by our fixtures
        self.root_page = Page.objects.filter(depth=1).first()
        if not self.root_page:
            # If root page doesn't exist, create it
            content_type = ContentType.objects.get_for_model(Page)
            self.root_page = Page.objects.create(
                title="Root",
                slug="root",
                depth=1,
                path="0001",
                content_type=content_type,
                url_path="/",
            )

        try:
            self.home_page = HomePage.objects.get(slug="home")
        except HomePage.DoesNotExist:
            locale = Locale.objects.first()
            if not locale:
                locale = Locale.objects.create(language_code="en")

            self.home_page = HomePage(
                title="Home",
                slug="home",
                path=self.root_page.path + "0001",
                depth=self.root_page.depth + 1,
                hero_title="Welcome to Our Site",
                hero_subtitle="Discover our services",
                hero_cta_text="Learn More",
                hero_cta_link="https://example.com",
                pricing_cta_link="https://example.com/pricing",
                locale=locale,
            )
            self.root_page.add_child(instance=self.home_page)

    def test_admin_login_required(self):
        """Test that admin pages require login."""
        # Try to access admin without logging in
        response = self.client.get("/admin/")

        # Should redirect to login page
        self.assertRedirects(response, "/admin/login/?next=/admin/")

        # Try to access pages admin
        response = self.client.get("/admin/pages/")

        # Should redirect to login page
        self.assertRedirects(response, "/admin/login/?next=/admin/pages/")

    def test_admin_with_login(self):
        """Test admin access with valid credentials."""
        # Login with the default superuser
        self.login()

        # Try to access admin
        response = self.client.get("/admin/")

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

        # Try to access pages admin
        response = self.client.get("/admin/pages/")

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

    def test_page_preview(self):
        """Test page preview functionality."""
        # Login as admin
        self.login()

        # Create a test page but don't publish it yet
        landing_page = LandingPage(
            title="Preview Test Page",
            slug="preview-test",
            hero_title="Preview Hero",
            hero_subtitle="This is a preview test",
            hero_cta_text="Preview Button",
            hero_cta_link="https://example.com/preview",
            schema_org_type="WebPage",
            parent=self.home_page,
        )
        self.home_page.add_child(instance=landing_page)

        # Get the preview URL
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_edit", args=[landing_page.id]
        )

        # Access the preview
        response = self.client.get(preview_url)

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

        # Check preview contains the unpublished content
        self.assertContains(response, "Preview Hero")


@pytest.mark.views
def test_page_serve_hooks(client, home_page, site):
    """Test that serve_page hooks work."""
    # Set up a hook function to test with
    hook_was_called = False

    def test_hook(page, request, serve_args, serve_kwargs):
        nonlocal hook_was_called
        hook_was_called = True
        return None  # Don't modify the response

    # Register our hook temporarily
    with hooks.register_temporarily("before_serve_page", test_hook):
        # Access the homepage
        response = client.get("/")

        # Check the hook was called
        assert hook_was_called is True

        # Check the page still rendered
        assert response.status_code == 200


@pytest.mark.views
def test_url_routing(client, home_page, site):
    """Test URL routing to correct pages."""
    # Create two landing pages with different slugs
    locale = Locale.objects.first()

    # Page 1 with slug 'page-one'
    page_one = LandingPage(
        title="Page One",
        slug="page-one",
        hero_title="Page One Title",
        hero_cta_link="https://example.com",
        schema_org_type="WebPage",
        locale=locale,
    )
    home_page.add_child(instance=page_one)

    # Page 2 with slug 'page-two'
    page_two = LandingPage(
        title="Page Two",
        slug="page-two",
        hero_title="Page Two Title",
        hero_cta_link="https://example.com",
        schema_org_type="WebPage",
        locale=locale,
    )
    home_page.add_child(instance=page_two)

    # Test routing to first page
    response = client.get("/page-one/")
    assert response.status_code == 200
    assert "Page One Title" in response.content.decode("utf-8")

    # Test routing to second page
    response = client.get("/page-two/")
    assert response.status_code == 200
    assert "Page Two Title" in response.content.decode("utf-8")

    # Test non-existent page returns 404
    response = client.get("/non-existent-page/")
    assert response.status_code == 404
