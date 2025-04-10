# Modify your search/__init__.py to explicitly make views importable
default_app_config = 'search.apps.SearchConfig'

# Remove this line that causes circular imports
# from . import views