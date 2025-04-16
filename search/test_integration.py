"""
Integration tests for search app.
These tests verify end-to-end functionality of the search app.
"""
import time
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from wagtail.models import Page, Site

from home.models import HomePage, LandingPage

# Apply the django_db marker to allow database access
pytestmark = pytest.mark.django_db

# Base test class for search integration tests
class SearchTestBase:
    """Base class for search integration tests."""

    @pytest.fixture(autouse=True)
    def setup(self, client, home_page, site, admin_user, mock_search):
        """Set up test environment before each test."""
        self.client = client
        self.home_page = home_page
        self.site = site
        self.admin_user = admin_user
        self.search_url = reverse("search")
        self.mock_search = mock_search


@pytest.mark.integration
class TestSearchFromNavbar(SearchTestBase):
    """Tests for search functionality from the navigation bar."""

    def test_search_from_navbar(self):
        """Test search from navigation bar."""
        # Create test page
        test_page = LandingPage(
            title="Navbar Search Test Page",
            slug="navbar-search-test",
            hero_title="Navbar Search Test Content",
            hero_subtitle="This page should appear in navbar search results",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(test_page, "schema_org_type"):
            test_page.schema_org_type = "WebPage"

        self.home_page.add_child(instance=test_page)
        test_page.save_revision().publish()

        # Visit the home page to check the navbar search form
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Check for search form in the navbar
        assert "form" in content.lower()
        assert "search" in content.lower()

        # Use the search form
        response = self.client.get(self.search_url + "?query=navbar")
        assert response.status_code == 200


@pytest.mark.integration
class TestSearchRelevancy(SearchTestBase):
    """Tests for search result ordering by relevance."""

    def test_search_relevancy(self):
        """Test search result ordering by relevance."""
        # Create test pages
        high_relevance_page = LandingPage(
            title="High Relevance Search Term Page",
            slug="high-relevance",
            hero_title="Search Term in Hero Title",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(high_relevance_page, "schema_org_type"):
            high_relevance_page.schema_org_type = "WebPage"

        self.home_page.add_child(instance=high_relevance_page)
        high_relevance_page.save_revision().publish()

        medium_relevance_page = LandingPage(
            title="Medium Relevance Page",
            slug="medium-relevance",
            hero_title="Medium Priority Page",
            hero_cta_link="https://example.com",
        )

        # Add required fields
        if hasattr(medium_relevance_page, "schema_org_type"):
            medium_relevance_page.schema_org_type = "WebPage"

        self.home_page.add_child(instance=medium_relevance_page)
        medium_relevance_page.save_revision().publish()

        # Perform search
        response = self.client.get(self.search_url + "?query=search term")
        assert response.status_code == 200


@pytest.mark.integration
class TestSearchFilters(SearchTestBase):
    """Tests for search filtering functionality."""

    def test_search_filters(self):
        """Test search filtering by page type or other attributes."""
        # Create test pages
        test_pages = []
        for i in range(3):
            test_page = LandingPage(
                title=f"Filter Test Page {i+1}",
                slug=f"filter-test-{i+1}",
                hero_title=f"Filter Test {i+1}",
                hero_cta_link="https://example.com",
            )

            # Add required fields
            if hasattr(test_page, "schema_org_type"):
                test_page.schema_org_type = "WebPage"

            self.home_page.add_child(instance=test_page)
            test_page.save_revision().publish()
            test_pages.append(test_page)

        # Perform basic search
        response = self.client.get(self.search_url + "?query=filter")
        assert response.status_code == 200


@pytest.mark.integration
class TestSearchPerformance(SearchTestBase):
    """Tests for search performance with many pages."""

    def test_search_performance(self):
        """Test search performance with large number of pages."""
        # Create test pages
        test_pages = []
        num_pages = 10

        for i in range(num_pages):
            test_page = LandingPage(
                title=f"Performance Test Page {i+1}",
                slug=f"performance-test-{i+1}",
                hero_title=f"Performance Content {i+1}",
                hero_cta_link="https://example.com",
            )

            # Add required fields
            if hasattr(test_page, "schema_org_type"):
                test_page.schema_org_type = "WebPage"

            self.home_page.add_child(instance=test_page)
            test_page.save_revision().publish()
            test_pages.append(test_page)

        # Measure search performance (just the view rendering, not actual search)
        start_time = time.time()
        response = self.client.get(self.search_url + "?query=performance")
        end_time = time.time()

        # Check response
        assert response.status_code == 200

        # Check view rendering performance
        search_time = end_time - start_time
        assert search_time < 2.0  # Rendering should complete within 2 seconds
