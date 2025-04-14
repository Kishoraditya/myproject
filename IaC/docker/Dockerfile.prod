FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=myproject.settings.docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Copy project
COPY . .

# Create URL fixing script 
RUN echo '#!/bin/bash\n\n# Script to fix URL patterns in any Django project structure\necho "Looking for urls.py files to fix..."\n\n# Find all urls.py files in the project\nfor urlfile in $(find /app -name "urls.py"); do\n    echo "Checking $urlfile"\n    \n    # Check if the file contains the problematic import\n    if grep -q "from search import views as search_views" "$urlfile"; then\n        echo "Fixing import in $urlfile"\n        sed -i "s/from search import views as search_views/from search.views import search/" "$urlfile"\n        \n        # Fix the URL pattern too\n        sed -i "s/path(\"search\\/\", search_views.search, name=\"search\")/path(\"search\\/\", search, name=\"search\")/" "$urlfile"\n        echo "Fixed $urlfile"\n    fi\ndone\n\necho "URL fixing complete!"' > /app/fix_urls.sh && \
    chmod +x /app/fix_urls.sh

# Create the search app configuration if it doesn't exist
RUN mkdir -p search && \
    touch search/__init__.py && \
    echo 'from django.apps import AppConfig\n\nclass SearchConfig(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "search"' > search/apps.py && \
    echo 'from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator\nfrom django.template.response import TemplateResponse\nfrom wagtail.models import Page\n\ndef search(request):\n    search_query = request.GET.get("query", None)\n    page = request.GET.get("page", 1)\n    if search_query:\n        search_results = Page.objects.live().search(search_query)\n    else:\n        search_results = Page.objects.none()\n    paginator = Paginator(search_results, 10)\n    try:\n        search_results = paginator.page(page)\n    except PageNotAnInteger:\n        search_results = paginator.page(1)\n    except EmptyPage:\n        search_results = paginator.page(paginator.num_pages)\n    return TemplateResponse(request, "search/search.html", {"search_query": search_query, "search_results": search_results})' > search/views.py && \
    /app/fix_urls.sh

# Create static files directory and collect static files
RUN mkdir -p /app/staticfiles && \
    python manage.py collectstatic --noinput

# Create entrypoint script
RUN echo '#!/bin/bash\nset -e\n\necho "Waiting for database to be ready..."\n# Give the database some time to start up\nsleep 5\n\necho "Running database migrations..."\npython manage.py migrate --noinput\n\necho "Creating cache tables..."\npython manage.py createcachetable\n\necho "Starting application server..."\nexec "$@"' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
    
# Run gunicorn with static files serving
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
