import os


def site_settings(request):
    """
    Adds site settings variables to the context from the database SEO settings.
    """
    # Import here to avoid circular imports
    from home.models import SEOSettings

    # Try to get the first SEO settings instance
    seo_settings = SEOSettings.objects.first()

    # Check if we're in a test environment
    is_test = "PYTEST_CURRENT_TEST" in os.environ

    # Use database values if available, otherwise use empty defaults
    # This allows admin to add values through the admin interface
    if seo_settings:
        return {
            "site_name": seo_settings.site_name,
            "site_description": seo_settings.default_description,
            "is_test_environment": is_test,
        }
    else:
        return {
            "site_name": "",
            "site_description": "",
            "is_test_environment": is_test,
        }
