# Modify your search/__init__.py to explicitly make views importable
default_app_config = "search.apps.SearchConfig"

# Add an empty dictionary for app configs
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Remove this line that causes circular imports
# from . import views
