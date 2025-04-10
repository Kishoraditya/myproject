from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from wagtail.models import Locale, Page, Site

from home.models import HomePage  # Adjust import based on your actual models


class HomePageTests(TestCase):
    def setUp(self):
        # Ensure default locale exists
        if not Locale.objects.exists():
            Locale.objects.create(language_code="en")

        # Create the root page structure
        # First, check if we already have a root page
        try:
            self.root_page = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            # Get the content type for Page model
            page_content_type = ContentType.objects.get_for_model(Page)

            # Create a root page
            self.root_page = Page.objects.create(
                title="Root",
                slug="root",
                depth=1,
                path="0001",
                content_type=page_content_type,
                url_path="/",
            )

        # Create a home page as child of root
        try:
            self.home_page = HomePage.objects.get(slug="home")
        except HomePage.DoesNotExist:
            self.home_page = HomePage(
                title="Home",
                slug="home",
            )
            self.root_page.add_child(instance=self.home_page)

        # Create a site pointing to the home page
        if not Site.objects.exists():
            Site.objects.create(
                hostname="localhost", root_page=self.home_page, is_default_site=True
            )

    def test_can_create_homepage(self):
        # Test that our setup created the homepage correctly
        retrieved_page = Page.objects.get(slug="home")
        self.assertEqual(retrieved_page.title, "Home")
        self.assertTrue(isinstance(retrieved_page.specific, HomePage))

    def test_homepage_renders(self):
        # Test that the homepage renders correctly
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # Add more assertions as needed
