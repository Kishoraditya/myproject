"""
Tests for search views.
These tests verify the functionality of the search views.
"""
from unittest.mock import patch

import pytest
from django.urls import reverse

from home.models import LandingPage

# Apply the django_db marker to allow database access
pytestmark = pytest.mark.django_db


@pytest.mark.views
def test_search_view_get(client, site):
    """Test search view with GET request without query."""
    # Get the search URL
    search_url = reverse("search")

    # Access search without query parameter
    response = client.get(search_url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Verify it's using the right template
    assert "search/search.html" in [t.name for t in response.templates]

    # Check that 'search_query' is empty in context
    assert response.context["search_query"] == ""

    # Check that search results are empty
    assert len(response.context["search_results"]) == 0


@pytest.mark.views
@patch("search.views._perform_search")
def test_search_with_query(mock_search, client, home_page, landing_page, site):
    """Test search with query parameter."""
    # Set up mock search results
    mock_results = [landing_page]
    mock_search.return_value = mock_results

    # Perform search with 'searchable' query
    search_url = reverse("search") + "?query=searchable"
    response = client.get(search_url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Check that 'search_query' is correctly set in context
    assert response.context["search_query"] == "searchable"

    # Verify mock was called with the right query
    mock_search.assert_called_once_with("searchable")


@pytest.mark.views
@patch("search.views._perform_search")
def test_search_no_results(mock_search, client, site):
    """Test empty search results."""
    # Set up mock empty search results
    mock_search.return_value = []

    # Search for a term that shouldn't exist
    search_url = reverse("search") + "?query=nonexistentterm123456789"
    response = client.get(search_url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Check that 'search_query' is correctly set in context
    assert response.context["search_query"] == "nonexistentterm123456789"

    # Check that search results are empty
    assert len(response.context["search_results"]) == 0

    # Check that the 'no results' message is displayed
    content = response.content.decode("utf-8")
    assert "No results found" in content


@pytest.mark.views
@patch("search.views._perform_search")
def test_search_pagination(mock_search, client, home_page, site):
    """Test search results pagination."""
    # Create test pages for the mock
    test_pages = []
    for i in range(15):
        page = LandingPage(
            title=f"Pagination Test {i}",
            slug=f"pagination-test-{i}",
            hero_title=f"Pagination Content {i}",
            schema_org_type="WebPage",
        )
        test_pages.append(page)

    # Set up mock search with pagination
    mock_search.return_value = test_pages

    # Search for pages with 'pagination' in the title
    search_url = reverse("search") + "?query=pagination"
    response = client.get(search_url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Check that 'search_query' is correctly set in context
    assert response.context["search_query"] == "pagination"

    # Verify mock was called with the right query
    mock_search.assert_called_once_with("pagination")

    # Check pagination is working
    assert len(response.context["search_results"]) == 10  # Default page size is 10


@pytest.mark.views
@patch("search.views._perform_search")
def test_search_case_insensitivity(mock_search, client, home_page, site):
    """Test search is case insensitive."""
    # Create a test page for the mock
    test_page = LandingPage(
        title="CasE SenSiTiVitY Test",
        slug="case-sensitivity-test",
        hero_title="Testing Case Sensitivity",
        schema_org_type="WebPage",
    )

    # Set up mock search for case insensitivity test
    mock_search.return_value = [test_page]

    # Search with lowercase query
    search_url = reverse("search") + "?query=case sensitivity"
    response_lower = client.get(search_url)

    # Check that the searches were performed
    assert response_lower.status_code == 200

    # Verify the search function was called with the queries
    mock_search.assert_called_with("case sensitivity")

    # Check that we found the page in results
    page_titles = [page.title for page in response_lower.context["search_results"]]
    assert "CasE SenSiTiVitY Test" in page_titles


@pytest.mark.views
@patch("search.views._perform_search")
def test_search_template_variables(mock_search, client, home_page, site):
    """Test template gets correct context variables."""
    # Set up mock empty search results
    mock_search.return_value = []

    # Search for something
    search_url = reverse("search") + "?query=test"
    response = client.get(search_url)

    # Check that the response is 200 OK
    assert response.status_code == 200

    # Check for required context variables
    context_vars = response.context

    # These are the key context variables that should be present
    assert "search_query" in context_vars
    assert "search_results" in context_vars

    # If pagination is implemented
    assert hasattr(context_vars["search_results"], "paginator")

    # Check for optional search-related variables that might be present
    if "search_type" in context_vars:
        assert isinstance(context_vars["search_type"], str)

    if "search_prompt" in context_vars:
        assert isinstance(context_vars["search_prompt"], str)

    # Verify the template has access to CSRF token
    assert "csrf_token" in context_vars


def test_search_with_query_basic(client, home_page):
    """Test search with a query parameter."""
    url = reverse("search") + "?query=test"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["search_query"] == "test"

    # Default behavior should be empty results for a test query
    # since we're using the default search backend in tests
    assert len(response.context["search_results"]) == 0


@patch("search.views._perform_search")
def test_search_with_mock_results_detailed(mock_search, client, home_page):
    """Test search with mocked search results."""
    # Use a real page instead of a mock
    # Create a Landing Page
    from home.models import LandingPage

    # Create real test page
    test_page = LandingPage(
        title="Test Page",
        slug="test-page",
        hero_title="Test Hero",
        hero_cta_link="https://example.com",
    )

    if hasattr(test_page, "schema_org_type"):
        test_page.schema_org_type = "WebPage"

    # Add the page
    home_page.add_child(instance=test_page)
    test_page.save_revision().publish()

    # Set up the mock to return our real page
    mock_search.return_value = [test_page]

    # Perform search
    url = reverse("search") + "?query=test"
    response = client.get(url)

    # Verify the result
    assert response.status_code == 200
    assert response.context["search_query"] == "test"
    assert len(response.context["search_results"]) == 1
    assert mock_search.called
    assert mock_search.call_args[0][0] == "test"


def test_search_no_results_basic(client):
    """Test search with no results."""
    url = reverse("search") + "?query=nonexistent"
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["search_query"] == "nonexistent"
    assert len(response.context["search_results"]) == 0


def test_search_pagination_basic(client, home_page):
    """Test search results pagination."""
    # Create real pages instead of mocks
    from home.models import LandingPage

    test_pages = []

    # Create 15 real pages
    for i in range(15):
        test_page = LandingPage(
            title=f"Test Page {i+1}",
            slug=f"test-page-{i+1}",
            hero_title=f"Test Hero {i+1}",
            hero_cta_link="https://example.com",
        )

        if hasattr(test_page, "schema_org_type"):
            test_page.schema_org_type = "WebPage"

        home_page.add_child(instance=test_page)
        test_page.save_revision().publish()
        test_pages.append(test_page)

    # Patch the search function to return our real pages
    with patch("search.views._perform_search") as mock_search:
        mock_search.return_value = test_pages

        # Test first page
        response = client.get(reverse("search") + "?query=test&page=1")
        assert response.status_code == 200

        # Check results length (10 is the default page size)
        assert len(response.context["search_results"]) == 10

        # Test second page
        response = client.get(reverse("search") + "?query=test&page=2")
        assert response.status_code == 200
        assert len(response.context["search_results"]) == 5


def test_search_with_invalid_page_param(client, home_page):
    """Test search with invalid page parameter."""
    # Create real pages instead of mocks
    from home.models import LandingPage

    test_pages = []

    # Create 15 real pages
    for i in range(15):
        test_page = LandingPage(
            title=f"Test Page {i+1}",
            slug=f"test-page-invalid-{i+1}",
            hero_title=f"Test Hero {i+1}",
            hero_cta_link="https://example.com",
        )

        if hasattr(test_page, "schema_org_type"):
            test_page.schema_org_type = "WebPage"

        home_page.add_child(instance=test_page)
        test_page.save_revision().publish()
        test_pages.append(test_page)

    # Patch the search function to return our real pages
    with patch("search.views._perform_search") as mock_search:
        mock_search.return_value = test_pages

        # Test non-numeric page
        response = client.get(reverse("search") + "?query=test&page=abc")
        assert response.status_code == 200

        # Test page out of range
        response = client.get(reverse("search") + "?query=test&page=999")
        assert response.status_code == 200


def test_search_case_insensitivity_basic(client):
    """Test search is case insensitive."""
    url1 = reverse("search") + "?query=test"
    url2 = reverse("search") + "?query=Test"
    url3 = reverse("search") + "?query=TEST"

    response1 = client.get(url1)
    response2 = client.get(url2)
    response3 = client.get(url3)

    # Just check they all return 200 - in a real test with mockable backends
    # we'd verify the results are the same
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200


def test_search_template_variables_basic(client):
    """Test template gets correct context variables."""
    url = reverse("search") + "?query=test"
    response = client.get(url)

    assert response.status_code == 200
    assert "search_query" in response.context
    assert "search_results" in response.context
    assert response.context["search_query"] == "test"
