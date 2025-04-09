# Adapting IaC to an Existing Wagtail Project

This guide explains how to adapt the Infrastructure as Code (IaC) folder to an existing Wagtail project to deploy it on AWS with Cloudflare DNS.

## Prerequisites

- An existing Wagtail project with PostgreSQL database
- Docker installed locally
- AWS account (free tier eligible)
- Cloudflare account (free tier eligible)

## Step 1: Copy the IaC Folder

1. Copy the entire `IaC` folder from this project to the root of your existing Wagtail project:

   ```bash
   cp -r /path/to/myproject/IaC /path/to/your-project/
   ```

## Step 2: Update Project Specific Settings

1. Modify the Django app name in Terraform files:

   ```bash
   cd /path/to/your-project/IaC/terraform/environments
   # Replace "wagtail-app" with your app name in all tfvars.example files
   find . -name "*.tfvars.example" -exec sed -i 's/wagtail-app/your-app-name/g' {} \;
   ```

2. Update the Docker paths if necessary:
   - If your project uses a different structure than standard Wagtail, update the paths in `IaC/docker/Dockerfile.prod` and `IaC/docker/docker-compose.prod.yml`

3. Check health check endpoints:
   - Ensure your Wagtail app has a `/health/` endpoint
   - If not, add one or modify the health check paths in the Docker Compose and Terraform files

## Step 3: Ensure Required Django Settings

1. Make sure your Django settings include AWS S3 configuration:

   ```python
   # In your settings.py file for production
   if not DEBUG:
       # AWS S3 settings
       AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
       AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
       AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
       AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
       
       # S3 static settings
       STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
       
       # Media settings
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
   ```

2. Add the health check URL:

   ```python
   # In your urls.py
   from django.http import HttpResponse
   
   def health_check(request):
       return HttpResponse("OK")
       
   urlpatterns = [
       # ... your existing URLs
       path('health/', health_check, name='health_check'),
   ]
   ```

3. Update your requirements.txt to include:

   ```bash
   django-storages
   boto3
   gunicorn
   ```

## Step 4: Adapt Docker Files (if needed)

1. If your project has specific dependencies beyond standard Wagtail, update the Dockerfile:

   ```bash
   # Edit the Dockerfile to add your specific system dependencies
   vi IaC/docker/Dockerfile.prod
   ```

2. If your project uses a different entrypoint or command than standard gunicorn, update the CMD:

   ```dockerfile
   # Example for a different command
   CMD ["gunicorn", "your_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
   ```

## Step 5: Configure Database Settings

Ensure your Django settings properly read database credentials from environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## Step 6: Deploy Your Project

Now follow the standard deployment guide:

1. Set up your credentials:

   ```bash
   cp IaC/credentials-example.env IaC/credentials.env
   # Edit credentials.env with your actual values
   vi IaC/credentials.env
   ```

2. Deploy to your chosen environment:

   ```bash
   cd IaC
   chmod +x deploy.sh
   ./deploy.sh --environment development
   ```

## Step 7: Set Up CI/CD in Your Repository

1. Copy the GitHub Actions workflows to your project:

   ```bash
   mkdir -p .github/workflows
   cp IaC/cicd/github-actions/*.yml .github/workflows/
   ```

2. Add required secrets to your GitHub repository (as outlined in the deployment guide)

## Troubleshooting

- **Build errors**: Check that your Dockerfile correctly sets up your specific project
- **Runtime errors**: Check CloudWatch logs for application errors
- **Database errors**: Verify that your app properly uses the environment variables for database configuration
- **Static files errors**: Ensure boto3 and django-storages are properly configured
