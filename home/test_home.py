from wagtail.models import Page
from wagtail.models.i18n import Locale
from home.models import HomePage
from django.test import TestCase


class HomePageTests(TestCase):
    def setUp(self):
        # Ensure default locale exists
        if not Locale.objects.exists():
            Locale.objects.create(language_code="en")

        # Ensure the root page exists
        self.root_page = Page.objects.get_or_create(title="Root", slug="root")[0]

        # Create a homepage if it does not exist
        if not HomePage.objects.exists():
            self.home_page = HomePage(title="Home", slug="home")
            self.root_page.add_child(instance=self.home_page)
            self.home_page.save()
        else:
            self.home_page = HomePage.objects.first()

    def test_can_create_homepage(self):
        root_page = Page.objects.get(id=self.root_page.id)
        self.assertIsNotNone(root_page)

    def test_homepage_renders(self):
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)


class HomePageModelTests(TestCase):
    def test_homepage_model_fields(self):
        # Create a homepage
        home_page = HomePage(title="Test Home", body="<p>Test content</p>")

        # Check field values
        self.assertEqual(home_page.title, "Test Home")
        self.assertEqual(home_page.body, "<p>Test content</p>")
