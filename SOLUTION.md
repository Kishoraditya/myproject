# Solution: Fixing AppRegistryNotReady Errors in Django Tests

## Problem

When running tests in a Django project (especially with Wagtail), you may encounter `AppRegistryNotReady` errors. 
This happens when Django models are imported at the module level before Django's app registry is fully initialized.

Common error message:
```
django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
```

This often occurs when:
1. Models are imported at the module level in test files
2. Tests are run with `pytest` without proper Django initialization
3. Wagtail models are used before the app registry is ready

## Solution

We implemented a comprehensive solution with the following components:

### 1. Django Ready Fixture

We created an auto-use session-scoped fixture in `conftest.py` that ensures Django is fully initialized before any tests run:

```python
@pytest.fixture(scope="session", autouse=True)
def django_ready():
    """Ensure Django is fully initialized before any tests run."""
    import django
    if not django.apps.apps.ready:
        django.setup()
    return True
```

### 2. Custom Test Runner Script

We created `run_tests.py` and `run_tests.bat` that properly initialize Django before running any tests:

```python
#!/usr/bin/env python
"""
Utility script to run tests with proper Django initialization.
This helps prevent AppRegistryNotReady errors.
"""
import os
import sys
import subprocess

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings.test")

# Initialize Django
import django
django.setup()

def main():
    """Run pytest with the given args."""
    # Default pytest args if none provided
    pytest_args = sys.argv[1:] or ["-v"]
    
    # Always use the test settings
    if "--ds" not in " ".join(pytest_args):
        pytest_args = ["--ds=myproject.settings.test"] + pytest_args
        
    # Run pytest
    result = subprocess.run(["pytest"] + pytest_args)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

### 3. Move Model Imports to Module Level

We updated all test files to import models at the module level instead of inside test functions, now that Django is properly initialized before any tests run:

```python
# Before
def test_something():
    from myapp.models import MyModel  # This could cause AppRegistryNotReady
    
# After
from myapp.models import MyModel  # Now safe with django_ready fixture

def test_something():
    # Use the imported model
```

### 4. Mock Complex Functionality

For complex functionality like search that often relies on database structures that might not be available during tests, we implemented a mockable architecture:

1. Refactored `search/views.py` to use a testable helper function:
   ```python
   def _perform_search(search_query):
       """Helper function to perform the search, making it easier to mock in tests."""
       if search_query:
           return Page.objects.live().search(search_query)
       return Page.objects.none()
   ```

2. Updated tests to mock this function:
   ```python
   @patch('search.views._perform_search')
   def test_search_with_query(mock_search, client):
       mock_results = [test_page]
       mock_search.return_value = mock_results
       
       response = client.get('/search/?query=test')
       mock_search.assert_called_once_with('test')
   ```

### 5. Test Settings

Our `test.py` settings include important optimizations:
- In-memory SQLite database
- Disabled migrations
- Faster password hasher
- In-memory file storage

### Results

With these changes:
- All tests now run without AppRegistryNotReady errors
- Search tests are fast and reliable, without needing real search indexes
- Test organization is consistent and follows best practices
- Test execution is significantly faster

## Best Practices

1. Always use the `run_tests.py` script to run tests
2. Import models at the module level in test files
3. Use mocking for complex functionality like search
4. Keep test settings optimized for speed and reliability
5. Skip tests that require complex setup until needed

## Future Improvements

1. Complete the admin tests with proper Wagtail setup
2. Add fixtures for creating test users with different permission levels
3. Implement factory functions for test data generation
4. Add coverage reporting to the test runner 