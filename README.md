# My Wagtail Project

A production-ready Wagtail Django project with PostgreSQL and test-driven development setup.

## Development Setup

1. Clone the repository
2. Run the setup script:

   ```bash
   ./setup.sh
   ```

3. Start the development server:

   ```bash
   python manage.py runserver

   ```bash
4. Visit [http://localhost:8000](http://localhost:8000) in your browser

## Running Tests

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
coverage run -m pytest
coverage report
coverage html  # generates HTML report
```

## Production Deployment

1. Set up environment variables in .env file
2. Build and run with Docker Compose:

   ```bash
   docker-compose up -d
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Step 18: Run migrations and start the server

```bash
python manage.py migrate 
```

```bash
python manage.py createsuperuser
```

```bash
python manage.py runserver

```

# Testing Infrastructure

The project includes a robust testing infrastructure to ensure code quality and functionality. Key features:

## Enhanced Test Runner

A custom test runner (`run_tests.py` and `run_tests.bat`) is provided to ensure proper Django initialization and avoid common issues like `AppRegistryNotReady` errors. Use these scripts instead of running pytest directly:

```bash
# Run all tests
python run_tests.py

# Run specific tests
python run_tests.py home/test_models.py::test_homepage_creation
```

## Mockable Search

The search functionality has been refactored to be easily mockable in tests, avoiding database-related issues with search indexes. See `search/test_views.py` for examples of how to test search functionality without relying on actual search backends.

## Django Ready Fixture

A `django_ready` fixture is automatically applied to all tests to ensure Django is fully initialized before tests run. This prevents common initialization issues when importing models.

## Test Settings

The `myproject/settings/test.py` file contains test-specific settings like:

- In-memory SQLite database for faster tests
- Disabled migrations for better performance
- MD5 password hasher for speed
- In-memory file storage

See `docs/testing.md` for more detailed documentation on the testing infrastructure.
