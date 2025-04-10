   # Modify your search/__init__.py to explicitly make views importable
   default_app_config = 'search.apps.SearchConfig'
   
   # Add this line to expose the views module
   from . import views