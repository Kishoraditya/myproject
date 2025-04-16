import pytest


# Add autouse fixture to ensure Django is fully initialized
@pytest.fixture(scope="session", autouse=True)
def django_ready():
    """Ensure Django is fully initialized before any tests run."""
    import django

    if not django.apps.apps.ready:
        django.setup()
    return True


# Move imports inside fixtures to avoid AppRegistryNotReady errors


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Configure database for testing."""
    # This fixture inherits from pytest-django's django_db_setup
    # We can add custom database setup for all tests here

    # Use the same database configuration as in dev/base settings
    # The test_ prefix is automatically added by Django

    with django_db_blocker.unblock():
        # Import test settings function to set up SQLite FTS
        from django.db import connection

        # Create FTS tables if needed
        if connection.vendor == "sqlite":
            with connection.cursor() as cursor:
                try:
                    # Create FTS tables manually
                    cursor.execute(
                        "CREATE VIRTUAL TABLE IF NOT EXISTS wagtailsearch_indexentry_fts "
                        'USING FTS5(autocomplete, title, body, content="wagtailsearch_indexentry")'
                    )
                except Exception:
                    pass  # Ignore errors if table already exists or can't be created


@pytest.fixture
def default_locale():
    """Create and return the default locale."""
    # Import here to ensure Django is fully initialized
    from django.conf import settings
    from wagtail.models import Locale

    # Get or create the default locale
    try:
        return Locale.objects.get(language_code=settings.LANGUAGE_CODE)
    except Locale.DoesNotExist:
        return Locale.objects.create(language_code=settings.LANGUAGE_CODE)


@pytest.fixture
def seo_settings():
    """Create and return SEO settings."""
    # Import here to ensure Django is fully initialized
    from home.models import SEOSettings

    # Get or create the SEO settings
    seo_settings, created = SEOSettings.objects.get_or_create(
        id=1,
        defaults={
            "site_name": "Test Site",
            "default_description": "Test description for SEO",
            "og_type": "website",
            "twitter_card": "summary_large_image",
            "twitter_site": "@testsite",
        },
    )
    return seo_settings


@pytest.fixture
def root_page(default_locale):
    """Create and return the root page."""
    # Import here to ensure Django is fully initialized
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page

    # The root page should be at depth=1
    try:
        return Page.objects.get(depth=1)
    except Page.DoesNotExist:
        page_content_type = ContentType.objects.get_for_model(Page)
        root_page = Page.objects.create(
            title="Root",
            slug="root",
            depth=1,
            path="0001",
            content_type=page_content_type,
            url_path="/",
            locale=default_locale,  # Set the locale
        )
        return root_page


@pytest.fixture
def home_page(root_page):
    """Create and return a home page."""
    # Import here to ensure Django is fully initialized
    from home.models import HomePage

    try:
        home_page = HomePage.objects.get(slug="home")
        return home_page
    except HomePage.DoesNotExist:
        home_page = HomePage(
            title="Home",
            slug="home",
            path=root_page.path + "0001",
            depth=root_page.depth + 1,
            hero_title="Welcome to Our Site",
            hero_subtitle="Discover our services",
            hero_cta_text="Learn More",
            hero_cta_link="https://example.com",
            pricing_cta_link="https://example.com/pricing",
        )
        root_page.add_child(instance=home_page)
        return home_page


@pytest.fixture
def landing_page(home_page):
    """Create and return a landing page."""
    # Import here to ensure Django is fully initialized
    from home.models import LandingPage

    try:
        landing_page = LandingPage.objects.get(slug="test-landing-page")
        return landing_page
    except LandingPage.DoesNotExist:
        landing_page = LandingPage(
            title="Test Landing Page",
            slug="test-landing-page",
            hero_title="Test Hero Title",
            hero_subtitle="Test Hero Subtitle",
            hero_cta_text="Click Here",
            hero_cta_link="https://example.com",
            meta_keywords="test, landing, page, seo",
            show_breadcrumbs=True,
            show_share_buttons=True,
        )
        home_page.add_child(instance=landing_page)
        return landing_page


@pytest.fixture
def site(home_page):
    """Create and return a site with home page as root."""
    # Import here to ensure Django is fully initialized
    from wagtail.models import Site

    # Create a site with the homepage as the root
    try:
        return Site.objects.get(is_default_site=True)
    except Site.DoesNotExist:
        return Site.objects.create(
            hostname="localhost",
            port=80,
            root_page=home_page,
            site_name="Test Site",
            is_default_site=True,
        )


@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    # Import here to ensure Django is fully initialized
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        admin = User.objects.get(username="admin")
        return admin
    except User.DoesNotExist:
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )
        return admin


@pytest.fixture
def client_with_admin(client, admin_user):
    """Return a client logged in as admin."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def wagtail_test_utils():
    """Return the WagtailTestUtils for login helpers."""
    from wagtail.test.utils import WagtailTestUtils

    return WagtailTestUtils


@pytest.fixture
def image_collection():
    """Create and return a collection for test images."""
    # Import here to ensure Django is fully initialized
    from wagtail.models import Collection

    try:
        collection = Collection.objects.get(name="Test Images")
        return collection
    except Collection.DoesNotExist:
        root_collection = Collection.get_first_root_node()
        collection = root_collection.add_child(name="Test Images")
        return collection


@pytest.fixture
def mock_search(monkeypatch):
    """Mock the Wagtail search backend to avoid SQLite FTS issues."""
    # Import here to ensure Django is fully initialized
    from unittest.mock import MagicMock

    from django.db import connection
    from wagtail.models import Page

    # First try to create the FTS tables if they don't exist
    if connection.vendor == "sqlite":
        with connection.cursor() as cursor:
            try:
                # Create FTS tables manually
                cursor.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS wagtailsearch_indexentry_fts "
                    'USING FTS5(autocomplete, title, body, content="wagtailsearch_indexentry")'
                )
            except Exception:
                pass  # Ignore errors if table already exists or can't be created

    # Create a mock search backend
    mock_backend = MagicMock()

    # Mock the search method to return actual pages but without using FTS
    def mock_search_method(query_string, *args, **kwargs):
        # A simple implementation that filters pages based on the query string
        # This avoids using FTS tables altogether
        if not query_string:
            return Page.objects.none()

        # Just use title search which should work across all page types
        # We can't use .filter() with specific page type fields directly
        # on the Page model because of the inheritance structure
        pages = Page.objects.live().filter(title__icontains=query_string)

        # Convert the query set to a list of specific pages
        # so we can check for the other fields after getting specific instances
        results = []
        for page in pages:
            specific_page = page.specific
            results.append(specific_page)

        # Also find pages by checking their specific type attributes
        # For each page type, we need a separate query
        from home.models import HomePage, LandingPage

        # Search in LandingPage-specific fields
        landing_pages = (
            LandingPage.objects.live().filter(title__icontains=query_string)
            | LandingPage.objects.live().filter(hero_title__icontains=query_string)
            | LandingPage.objects.live().filter(hero_subtitle__icontains=query_string)
        )

        # Search in HomePage-specific fields
        home_pages = (
            HomePage.objects.live().filter(title__icontains=query_string)
            | HomePage.objects.live().filter(hero_title__icontains=query_string)
            | HomePage.objects.live().filter(hero_subtitle__icontains=query_string)
        )

        # Combine all pages
        results.extend(
            [p for p in landing_pages if p.id not in [x.id for x in results]]
        )
        results.extend([p for p in home_pages if p.id not in [x.id for x in results]])

        # Convert back to a Page queryset
        if results:
            return Page.objects.filter(id__in=[p.id for p in results])

        return Page.objects.none()

    # Set the search method on the mock
    mock_backend.search = mock_search_method

    # Replace the get_search_backend function
    monkeypatch.setattr(
        "wagtail.search.backends.get_search_backend", lambda name=None: mock_backend
    )

    # Also patch the _perform_search function in the views module
    monkeypatch.setattr("search.views._perform_search", mock_search_method)

    return mock_backend
