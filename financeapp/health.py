"""
Provides health check endpoints for readiness and liveness of the application.

This module includes two endpoints:
1. Readiness: Checks the availability of critical dependencies like the database
   and cache to determine whether the application can handle requests.
2. Liveness: Confirms that the application is running and responsive.

The readiness endpoint performs detailed health checks to ensure the system's
dependencies are functioning as expected, while the liveness endpoint provides
a quick status check to verify that the application is up.

"""

import logging
from http import HTTPStatus
from uuid import uuid4

from django.core.cache import cache
from django.db import connection
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe
from psycopg import DatabaseError
from redis import RedisError

logger = logging.getLogger(__name__)


@never_cache
@require_safe
def readiness(request: HttpRequest) -> JsonResponse:
    """
    Indicates the readiness state of the application by checking the database and cache services.

    This function performs health checks for two critical components of the application:
    - Database: Ensures that the database connection is functional by executing a simple query.
    - Cache: Performs a basic round-trip check to confirm the cache service is operational.

    Returns:
        JsonResponse: A JSON response indicating the health status of the application. If all
        checks pass, the response contains a "healthy" status. If any check fails, the
        response contains an "unhealthy" status with an appropriate service unavailability
        HTTP status.

    Args:
        request (HttpRequest): The HTTP request object.

    Raises:
        DatabaseError: Raised if the database connection fails.
        RedisError: Raised if the cache round-trip test fails.
    """

    # Check if the database connection is ready
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except DatabaseError:
        logger.error("Database readiness check failed", exc_info=True)
        return JsonResponse({"status": "unhealthy"}, status=HTTPStatus.SERVICE_UNAVAILABLE)

    # Check if cache is ready
    try:
        key = f"readiness:{uuid4().hex}"
        cache.set(key, "ready", timeout=10)
        value = cache.get(key)
        cache.delete(key)
        if value != "ready":
            raise RedisError("Cache round-trip failed")
    except RedisError:
        logger.error("Cache readiness check failed", exc_info=True)
        return JsonResponse({"status": "unhealthy"})

    return JsonResponse({"status": "healthy"}, status=HTTPStatus.SERVICE_UNAVAILABLE)


@never_cache
@require_safe
def liveness(request: HttpRequest) -> JsonResponse:
    """
    Checks the liveness of the application by returning a simple JSON response.

    This function is intended to be used as a health check endpoint to ensure the
    application is running and responsive to incoming requests. It does not assess
    the overall health of integrations or complex dependencies but simply confirms
    the application's basic availability.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the key "status" with the value
        "alive".
    """
    return JsonResponse({"status": "alive"})