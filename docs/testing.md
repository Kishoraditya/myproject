# Running Tests

This document describes how to run tests for the `myproject` project.

## Overview

The project uses pytest with pytest-django for running tests. We've set up a custom testing infrastructure to ensure Django's app registry is properly initialized before tests run, preventing common issues like `AppRegistryNotReady` errors.

## Running Tests

### Using the run_tests script (Recommended)

The simplest way to run tests is using the provided `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run tests with verbosity
python run_tests.py -v

# Run specific test file
python run_tests.py home/test_models.py

# Run specific test function
python run_tests.py home/test_models.py::test_homepage_creation

# Run tests by marker
python run_tests.py -m views
```

On Windows, you can also use the provided batch file:

```
run_tests.bat -v
```

### Using pytest directly

If you prefer to use pytest directly, make sure to specify the Django settings module:

```bash
# Set Django settings module
set DJANGO_SETTINGS_MODULE=myproject.settings.test

# Run tests with Django settings
pytest --ds=myproject.settings.test
```

## Test Structure

Tests are organized by app, with test files prefixed with `test_`. For example:
- `home/test_models.py`: Tests for models in the home app
- `home/test_views.py`: Tests for views in the home app
- `search/test_views.py`: Tests for views in the search app

## Important Fixtures

The project provides several important fixtures:

- `django_ready`: Ensures Django is fully initialized before any tests run
- `django_db_setup`: Configures the test database
- `default_locale`: Creates and returns the default locale
- `root_page`: Creates and returns the root page
- `home_page`: Creates and returns a home page
- `landing_page`: Creates and returns a landing page
- `site`: Creates and returns a site with home page as root
- `admin_user`: Creates and returns an admin user
- `client_with_admin`: Returns a client logged in as admin

## Mocking Search Functionality

The search functionality is designed to be easily mockable for testing. Instead of relying on the actual search backend (which would require database setup for search indexes), we:

1. Created a `_perform_search` helper function in `search/views.py` that encapsulates search logic
2. In tests, we use a custom `mock_search` fixture to simulate the search functionality
3. The fixture creates an in-memory implementation of search that works with specific page types

This approach has several benefits:
- Tests run faster without needing to build search indexes
- Tests are more reliable and don't depend on search backend details
- Different search scenarios can be easily simulated

### Search Implementation for SQLite FTS

We've implemented a solution for the SQLite FTS (Full-Text Search) tables required by Wagtail:

1. In `test.py` settings, we create the required FTS virtual table:
```python
def setup_sqlite_fts():
    """Setup SQLite FTS tables after database creation."""
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            # Create FTS tables manually
            cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS wagtailsearch_indexentry_fts USING FTS5(autocomplete, title, body, content="wagtailsearch_indexentry")')
```

2. This function is called during test setup to ensure the FTS tables exist.

3. We also created a robust `mock_search` fixture in `conftest.py` that:
   - Handles both base Page fields and specific page type fields (like hero_title)
   - Works with our existing page types (HomePage, LandingPage)
   - Integrates with the search view to provide realistic search behavior

Example usage in a test:

```python
@pytest.mark.integration
def test_search_results(mock_search):
    # Create test pages with searchable content
    test_page = LandingPage(
        title="Searchable Test Page",
        hero_title="Searchable Content",
        hero_subtitle="This page should appear in search results",
    )
    
    # No need to manually mock - our fixture handles the search automatically
    response = client.get('/search/?query=searchable')
    assert response.status_code == 200
    assert 'Searchable Test Page' in response.content.decode('utf-8')
```

## Best Practices

1. Always use the `django_ready` fixture (it's applied automatically)
2. Import Django models at module level, not inside functions
3. Use the provided fixtures to set up test data
4. Use markers to categorize tests (`@pytest.mark.views`, `@pytest.mark.models`, etc.)
5. Use the `run_tests.py` script to ensure proper Django initialization
6. Mock complex functionality (like search) to make tests faster and more reliable
7. Use `unittest.mock.patch` to mock functionality when appropriate

## Troubleshooting

### AppRegistryNotReady Error

If you encounter `AppRegistryNotReady` errors, make sure you're using the `run_tests.py` script or have properly initialized Django before importing models. Our solution uses a session-scoped `django_ready` fixture that ensures Django is fully initialized.

### Missing Migrations

The test settings use `DisableMigrations` to speed up tests. If you need to test with migrations, modify the test settings accordingly.

### Database Errors

Test settings use an in-memory SQLite database. For complex database operations, you might need to switch to a file-based database in the test settings.

### Search-Related Errors

If you encounter errors related to search indexes or search tables, our project provides two solutions:

1. **Mocked search implementation**: We've created a custom `mock_search` fixture in `conftest.py` that implements search functionality without requiring the full search index tables. This is the preferred approach for most tests.

2. **SQLite FTS table creation**: For tests that need to interact more directly with search, we create the required SQLite FTS virtual table in the test settings and `django_db_setup` fixture. This handles the common error: `no such table: wagtailsearch_indexentry_fts`.

If you see errors about missing FTS tables, ensure:
- The `setup_sqlite_fts()` function is called in your test settings
- The test is using our `mock_search` fixture if it depends on search functionality
- You're using the project's test settings via `--ds=myproject.settings.test`

If you're creating custom search tests, look at the implementation in `search/test_integration.py` for examples of proper test setup. 