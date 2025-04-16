# Linting Guidelines

This document outlines how we handle code linting in the Shoshin project.

## Linting Tools

We use `flake8` for Python code linting with the following default commands:

```bash
# Check for critical errors only
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full linting check
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
```

## Critical Issues to Fix Immediately

The following issues should always be fixed as they can cause runtime errors:

1. **F821: Undefined name** - References to variables that don't exist
2. **E999: SyntaxError** - Invalid Python syntax
3. **F401: Unused imports** (when using specific features like patch decorators, add `# noqa: F401` comments)
4. **F811: Redefinition of unused name** - Functions/classes redefined without being used

## Recent Fixes

Recent linting improvements to the codebase include:

1. **test_run_tests.py**:
   - Added missing `unittest` import
   - Added explicit `os` and `sys` imports with `# noqa` comments

2. **test_health.py**:
   - Removed unused `connections` import

3. **test_browser.py**:
   - Removed unused `Page` and `HomePage` imports

4. **search/test_views.py**:
   - Removed unused imports (json, MagicMock, EmptyPage, etc.)
   - Renamed duplicate test functions to fix redefinition issues

5. **test_templates.py**:
   - Fixed f-string without placeholders

6. **settings/test.py**:
   - Added blank lines before class definition
   - Moved imports to top of file
   - Split long lines for readability

## Recommendations for Future Development

1. **Use Black for formatting** - Consider using Black for consistent code formatting
2. **Add pre-commit hooks** - Set up pre-commit hooks to check linting before commits
3. **Clean imports** - Only import what you need, use relative imports when appropriate
4. **Explicit noqa comments** - When ignoring linting errors, add specific codes (e.g., `# noqa: F401`)
5. **Split long lines** - Keep lines under 127 characters
6. **Add typing** - Consider adding type annotations to improve code quality

## Handling Common Issues

### When adding mocks and patches

When using `unittest.mock.patch` decorators, the imports being patched might appear unused:

```python
import os  # noqa: F401 - used in patch decorator
import sys  # noqa: F401 - used in patch decorator
from unittest.mock import patch

@patch("os.path.abspath")
@patch("sys.exit")
def test_function(self, mock_exit, mock_abspath):
    ...
```

### Django settings modules

Special case for Django settings modules using star imports:

```python
from .base import *  # noqa
``` 