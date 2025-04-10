#!/bin/bash

# Script to fix URL patterns in any Django project structure
echo "Looking for urls.py files to fix..."

# Find all urls.py files in the project
for urlfile in $(find /app -name "urls.py"); do
    echo "Checking $urlfile"
    
    # Check if the file contains the problematic import
    if grep -q "from search import views as search_views" "$urlfile"; then
        echo "Fixing import in $urlfile"
        sed -i 's/from search import views as search_views/from search.views import search/' "$urlfile"
        
        # Fix the URL pattern too
        sed -i 's/path("search\/", search_views.search, name="search")/path("search\/", search, name="search")/' "$urlfile"
        echo "Fixed $urlfile"
    fi
done

echo "URL fixing complete!" 