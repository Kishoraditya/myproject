from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.db.utils import OperationalError

@csrf_exempt
def health_check(request):
    """
    Basic health check endpoint that doesn't rely on the database if it's not ready.
    
    If the DB is ready, it will include a db_status: "ok".
    If the DB is not ready, it will still return 200 but with db_status: "not_available".
    """
    db_status = "not_available"
    
    # Check database connection
    try:
        db_conn = connections['default']
        db_conn.cursor()
        db_status = "ok"
    except OperationalError:
        # Database is not ready yet
        pass
    
    return JsonResponse({
        "status": "ok",
        "db_status": db_status
    }) 