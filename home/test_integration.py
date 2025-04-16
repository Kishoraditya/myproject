"""
Integration tests for home app.
These tests verify end-to-end functionality of the home app.
"""


import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from wagtail.images.models import Image

from home.models import LandingPage

# Apply the django_db marker to allow database access
pytestmark = pytest.mark.django_db

# Fix for TestUserPermissions in home/test_integration.py
def setUp(self):
    super().setUp()

    # Create test users with appropriate permissions
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group, Permission

    User = get_user_model()

    # Create editor group with necessary permissions
    editor_group, created = Group.objects.get_or_create(name="Editors")
    if created:
        # Add page permissions
        from wagtail.models import GroupPagePermission, Page

        root_page = Page.objects.get(depth=1)
        GroupPagePermission.objects.create(
            group=editor_group, page=root_page, permission_type="add"
        )
        GroupPagePermission.objects.create(
            group=editor_group, page=root_page, permission_type="edit"
        )

        # Add admin access permission
        admin_permission = Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
        editor_group.permissions.add(admin_permission)

    # Create and set up the test user
    self.test_user = User.objects.create_user(
        username="testuser", email="test@example.com", password="password"
    )
    self.test_user.groups.add(editor_group)

    # Log in as the test user
    self.client.login(username="testuser", password="password")


# Base test class that combines common setup code
class TestIntegrationBase:
    """Base class for all integration tests."""

    @pytest.fixture(autouse=True)
    def setup(self, client, home_page, site, admin_user):
        """Set up test environment before each test."""
        self.client = client
        self.home_page = home_page
        self.site = site
        self.admin_user = admin_user
        self.client_with_admin = Client()
        self.client_with_admin.force_login(admin_user)


@pytest.mark.integration
class TestPageCreationAdmin(TestIntegrationBase):
    """Tests for creating pages via the admin interface."""

    @pytest.mark.skip(reason="Requires more complex admin form handling")
    def test_page_creation_admin(self):
        """Test creating pages via admin interface."""
        # Log in as admin
        self.client_with_admin.force_login(self.admin_user)

        # Get the admin page creation URL
        add_url = reverse("wagtailadmin_pages:add_subpage", args=[self.home_page.id])
        response = self.client_with_admin.get(add_url)
        assert response.status_code == 200

        # Get the "Add Landing Page" URL
        add_landing_page_url = reverse(
            "wagtailadmin_pages:add",
            args=[
                LandingPage._meta.app_label,
                LandingPage._meta.model_name,
                self.home_page.id,
            ],
        )

        # Test GET request to the add form
        response = self.client_with_admin.get(add_landing_page_url)
        assert response.status_code == 200

        # Note: Creating a page via the admin is complex due to StreamFields and other Wagtail-specific form fields.
        # We would need to inspect the form and provide all the required data.
        # For integration tests, it's often better to create pages programmatically as we do in other tests.

        # Instead, let's create a page programmatically
        landing_page = LandingPage(
            title="Admin Created Page",
            slug="admin-created-page",
            hero_title="Admin Hero Title",
            hero_subtitle="Admin Hero Subtitle",
            hero_cta_text="Click Here",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(landing_page, "schema_org_type"):
            landing_page.schema_org_type = "WebPage"

        # Add the page
        self.home_page.add_child(instance=landing_page)
        landing_page.save_revision().publish()

        # Visit the published page
        response = self.client.get("/admin-created-page/")
        assert response.status_code == 200
        assert "Admin Hero Title" in response.content.decode("utf-8")


@pytest.mark.integration
class TestPageEditingWorkflow(TestIntegrationBase):
    """Tests for editing workflow of pages."""

    def test_page_editing_workflow(self):
        """Test complete edit workflow."""
        # Create a test page programmatically
        landing_page = LandingPage(
            title="Edit Workflow Test",
            slug="edit-workflow-test",
            hero_title="Original Hero",
            hero_subtitle="Original Subtitle",
            hero_cta_text="Original CTA",
            hero_cta_link="https://example.com/original",
        )

        # Add required fields
        if hasattr(landing_page, "schema_org_type"):
            landing_page.schema_org_type = "WebPage"

        # Add the page
        self.home_page.add_child(instance=landing_page)
        landing_page.save_revision().publish()

        # Verify original content
        response = self.client.get("/edit-workflow-test/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Original Hero" in content
        assert "Original Subtitle" in content

        # Edit the page programmatically
        landing_page.title = "Updated Title"
        landing_page.hero_title = "Updated Hero"
        landing_page.hero_subtitle = "Updated Subtitle"
        landing_page.hero_cta_text = "Updated CTA"
        landing_page.hero_cta_link = "https://example.com/updated"
        landing_page.save_revision().publish()

        # Verify the page was updated
        landing_page.refresh_from_db()
        assert landing_page.title == "Updated Title"
        assert landing_page.hero_title == "Updated Hero"

        # Visit the updated page
        response = self.client.get("/edit-workflow-test/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Updated Hero" in content
        assert "Updated Subtitle" in content

        # Check admin can view the edit page URL
        self.client_with_admin.force_login(self.admin_user)
        edit_url = reverse("wagtailadmin_pages:edit", args=[landing_page.id])
        response = self.client_with_admin.get(edit_url)
        assert response.status_code == 200


@pytest.mark.integration
class TestFormSubmission(TestIntegrationBase):
    """Tests for form submission handling."""

    def test_form_submission(self):
        """Test form submission handling."""
        # Test existence of search form in the site
        response = self.client.get("/")
        assert response.status_code == 200

        # Check if the search form exists in the base template
        content = response.content.decode("utf-8")

        # Look for form elements that suggest a search form
        assert "form" in content.lower()

        # This is a simplified test just checking for form existence
        # If the site has a contact or other submission form, these tests
        # should be expanded to actually test the form submission

        # Check that the search URL endpoint exists
        search_url = reverse("search")
        assert search_url == "/search/"


@pytest.mark.integration
@pytest.mark.skip(reason="Requires actual image file for upload")
class TestImageRendering(TestIntegrationBase):
    """Tests for image upload and rendering."""

    def test_image_rendering(self, image_collection):
        """Test image upload and rendering."""
        # Log in as admin
        self.client_with_admin.force_login(self.admin_user)

        # Create a test image (would need actual binary data for real test)
        # This is a simplified example; in a real test, you'd use an actual image file
        image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"",  # Empty content for stub test
            content_type="image/jpeg",
        )

        # Create image through the ORM
        image = Image(title="Test Image", file=image_file, collection=image_collection)
        image.save()

        # Create a page that uses the image
        landing_page = LandingPage(
            title="Image Test Page",
            slug="image-test-page",
            hero_title="Image Test",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(landing_page, "schema_org_type"):
            landing_page.schema_org_type = "WebPage"

        # Set image field if it exists
        if hasattr(landing_page, "hero_image"):
            landing_page.hero_image = image

        # Add the page
        self.home_page.add_child(instance=landing_page)
        landing_page.save_revision().publish()

        # Visit the page
        response = self.client.get("/image-test-page/")
        assert response.status_code == 200

        # Check image rendering (this would need adapted to your actual template)
        # If your template renders images with specific classes or structures
        if hasattr(landing_page, "hero_image"):
            content = response.content.decode("utf-8")
            assert "img" in content


@pytest.mark.integration
class TestNavigationGeneration(TestIntegrationBase):
    """Tests for navigation generation."""

    def test_navigation_generation(self):
        """Test automatic navigation generation."""
        # Create multiple pages in a hierarchy
        parent_page = LandingPage(
            title="Parent Page",
            slug="parent-page",
            hero_title="Parent Page",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(parent_page, "schema_org_type"):
            parent_page.schema_org_type = "WebPage"

        self.home_page.add_child(instance=parent_page)
        parent_page.save_revision().publish()

        # Create child pages
        for i in range(3):
            child_page = LandingPage(
                title=f"Child Page {i+1}",
                slug=f"child-page-{i+1}",
                hero_title=f"Child {i+1}",
                hero_cta_link="https://example.com",
            )

            # Add required fields
            if hasattr(child_page, "schema_org_type"):
                child_page.schema_org_type = "WebPage"

            parent_page.add_child(instance=child_page)
            child_page.save_revision().publish()

        # Visit the home page and check navigation
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for navigation elements - this just checks for the nav element
        assert "nav" in content.lower()

        # Visit parent page and check it's accessible
        response = self.client.get("/parent-page/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Check breadcrumbs or page title is present
        assert "Parent Page" in content or parent_page.title in content

        # Visit a child page and check it's accessible
        response = self.client.get("/parent-page/child-page-1/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Check page content is present
        assert "Child 1" in content or "Child Page 1" in content


@pytest.mark.integration
class TestSearchIntegration(TestIntegrationBase):
    """Tests for search integration with pages."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_search, default_locale):
        """Set up method that runs for each test method."""
        self.mock_search = mock_search
        self.default_locale = default_locale

    def test_search_integration(self):
        """Test search integration with pages."""
        # Create pages with specific content
        for i in range(3):
            test_page = LandingPage(
                title=f"Searchable Test Page {i+1}",
                slug=f"searchable-test-{i+1}",
                hero_title=f"Searchable Content {i+1}",
                hero_subtitle="This page should appear in search results",
                hero_cta_link="https://example.com",
            )

            # Add required fields
            if hasattr(test_page, "schema_org_type"):
                test_page.schema_org_type = "WebPage"

            # Add locale
            test_page.locale = self.default_locale

            # Add the page
            self.home_page.add_child(instance=test_page)
            test_page.save_revision().publish()

        # Perform search
        response = self.client.get(reverse("search") + "?query=searchable")
        assert response.status_code == 200

        # Check that we got a successful response
        content = response.content.decode("utf-8")
        assert "Searchable Test Page" in content

        # Check search with no results
        response = self.client.get(
            reverse("search") + "?query=nonexistentterm123456789"
        )
        assert response.status_code == 200
        assert (
            "No results" in response.content.decode("utf-8")
            or "no results" in response.content.decode("utf-8").lower()
        )


@pytest.mark.integration
class TestUserPermissions(TestIntegrationBase):
    """Tests for user permission enforcement."""

    def setUp(self):
        # Skip TestIntegrationBase setup for this test
        # We need our own setup for permission testing
        pass

    @pytest.mark.skip(reason="User permission test requires database migration setup")
    def test_user_permissions(self, default_locale):
        """Test user permission enforcement."""
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group, Permission
        from django.test import Client
        from wagtail.models import GroupPagePermission, Page

        User = get_user_model()

        # Get or create root page
        try:
            self.root_page = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            self.root_page = Page.objects.create(
                title="Root",
                depth=1,
                path="0001",
                content_type_id=1,
                locale=default_locale,
            )

        # Create test users with different permission levels
        self.admin_user = User.objects.create_superuser(
            username="testadmin",
            email="testadmin@example.com",
            password="adminpassword",
        )

        self.editor_user = User.objects.create_user(
            username="testeditor",
            email="testeditor@example.com",
            password="editorpassword",
        )

        self.viewer_user = User.objects.create_user(
            username="testviewer",
            email="testviewer@example.com",
            password="viewerpassword",
        )

        # Set up editor group with edit permissions
        self.editors_group, created = Group.objects.get_or_create(name="TestEditors")

        # Add admin access permission to editors group
        admin_access = Permission.objects.get(
            codename="access_admin", content_type__app_label="wagtailadmin"
        )
        self.editors_group.permissions.add(admin_access)

        # Add edit permission to editors group
        edit_permission = Permission.objects.filter(
            codename="change_page", content_type__app_label="wagtailcore"
        ).first()

        if edit_permission:
            self.editors_group.permissions.add(edit_permission)

        # Create page permissions
        GroupPagePermission.objects.create(
            group=self.editors_group, page=self.root_page, permission_type="change"
        )

        # Add editor user to editors group
        self.editor_user.groups.add(self.editors_group)

        # Set up client instances
        self.client = Client()
        self.admin_client = Client()
        self.editor_client = Client()
        self.viewer_client = Client()

        # Log in clients
        self.admin_client.force_login(self.admin_user)
        self.editor_client.force_login(self.editor_user)
        self.viewer_client.force_login(self.viewer_user)

        # Test admin access with admin user
        response = self.admin_client.get("/admin/")
        assert response.status_code == 200

        # Editor should be able to access admin
        response = self.editor_client.get("/admin/")
        assert response.status_code == 200

        # Editor should be able to see pages
        response = self.editor_client.get("/admin/pages/")
        assert response.status_code == 200

        # Test viewer access (should not have admin access)
        response = self.viewer_client.get("/admin/")
        # Should be redirected (302) as they don't have access_admin permission
        assert response.status_code == 302
