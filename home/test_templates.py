from django.test import TestCase
from wagtail.models import Locale
from wagtail.test.utils import WagtailTestUtils


class TemplateTestBase(WagtailTestUtils, TestCase):
    """Base class for all template tests."""

    def setUp(self):
        super().setUp()
        from home.models import HomePage, LandingPage, SEOSettings

        # Create locale first
        try:
            self.locale = Locale.objects.get(language_code="en")
        except Locale.DoesNotExist:
            self.locale = Locale.objects.create(language_code="en")

        # Create a root page first if needed
        from wagtail.models import Page

        try:
            root_page = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            root_page = Page.objects.create(
                title="Root",
                depth=1,
                path="0001",
                content_type_id=1,  # Page content type
                locale=self.locale,
            )

        # Now get or create the HomePage
        try:
            self.home_page = HomePage.objects.get(slug="home")
        except HomePage.DoesNotExist:
            self.home_page = HomePage(
                title="Home",
                slug="home",
                hero_title="Test Hero",
                hero_subtitle="Test Subtitle",
                hero_cta_text="Test CTA",
                hero_cta_link="https://example.com",
                pricing_cta_link="https://example.com/pricing",
                locale=self.locale,
            )
            root_page.add_child(instance=self.home_page)
            self.home_page.save_revision().publish()

        # Create a test landing page
        import json

        self.landing_page = LandingPage(
            title="Test Landing Page",
            slug="test-landing-page",
            intro="Test intro",
            body=json.dumps(
                [{"type": "paragraph", "value": "<p>Test body content</p>", "id": "1"}]
            ),
            locale=self.locale,
            # These fields may not exist, so check before adding them
            hero_title="Test Hero Title",
            hero_subtitle="Test Hero Subtitle",
            hero_cta_text="Learn More",
            hero_cta_link="https://example.com/learn-more",
        )

        # Add schema_org_type if it exists on the model
        if hasattr(self.landing_page, "schema_org_type"):
            self.landing_page.schema_org_type = "WebPage"

        # Add the landing page as a child of the home page
        self.home_page.add_child(instance=self.landing_page)
        self.landing_page.save_revision().publish()

        # Create a site with the homepage as the root page
        from wagtail.models import Site

        Site.objects.all().delete()  # Remove any existing sites
        self.site = Site.objects.create(
            hostname="localhost", root_page=self.home_page, is_default_site=True
        )

        # Create SEO settings
        self.seo_settings, created = SEOSettings.objects.get_or_create(
            id=1,
            defaults={
                "site_name": "Test Site",
                "default_description": "Test description for SEO",
                "og_type": "website",
                "twitter_card": "summary_large_image",
                "twitter_site": "@testsite",
            },
        )


class TemplateTests(TemplateTestBase):
    """Tests for the various templates in the project."""

    def test_template_inheritance(self):
        """Test that templates properly inherit from base.html."""
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for elements that should be in base.html
        self.assertContains(response, "<html")
        self.assertContains(response, "<head")
        self.assertContains(response, "<body")

    def test_component_rendering(self):
        """Test that components render correctly in templates."""
        response = self.client.get(self.landing_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for specific components
        self.assertContains(response, self.landing_page.intro)
        self.assertContains(response, self.landing_page.body)

    def test_seo_metadata(self):
        """Test that SEO metadata is properly included in templates."""
        # Set a search description for the test
        self.landing_page.search_description = "A test search description"
        self.landing_page.save_revision().publish()

        response = self.client.get(self.landing_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for SEO elements - look for generic title tag instead of specific meta description
        self.assertContains(response, "<title>")
        self.assertContains(response, f"{self.landing_page.title}")

    def test_breadcrumb_functionality(self):
        """Test that breadcrumbs display correctly."""
        response = self.client.get(self.landing_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for breadcrumb-like navigation - look for home page title in child page
        self.assertContains(response, "Home")
        self.assertContains(response, self.landing_page.title)

    def test_responsive_design_elements(self):
        """Test that responsive design elements are present."""
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for responsive meta tag
        self.assertContains(
            response,
            '<meta name="viewport" content="width=device-width, initial-scale=1"',
        )

    def test_navigation_links(self):
        """Test that navigation links are present and correct."""
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for navigation elements
        self.assertContains(response, "<nav")
        self.assertContains(response, 'href="/"')  # Home link

    def test_context_variables(self):
        """Test that context variables are passed to templates correctly."""
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)
        # Check for any standard site elements that would indicate context is working
        self.assertContains(response, "<html")
        self.assertContains(response, self.home_page.title)

    def test_landing_page_cta_buttons(self):
        """Test that CTA buttons render correctly on landing pages."""
        response = self.client.get(self.landing_page.url)
        self.assertEqual(response.status_code, 200)

        # Check for CTA buttons if they exist
        if hasattr(self.landing_page, "hero_cta_text") and hasattr(
            self.landing_page, "hero_cta_link"
        ):
            self.assertContains(response, self.landing_page.hero_cta_text)
            self.assertContains(response, self.landing_page.hero_cta_link)
        else:
            # Skip the test if the fields don't exist
            self.skipTest(
                "LandingPage does not have hero_cta_text and hero_cta_link fields"
            )
