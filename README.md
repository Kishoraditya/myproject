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
