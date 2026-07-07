"""
Shared rate limiter instance. Applied per-route (not globally) so only
sensitive/brute-forceable endpoints (login, signup, forgot-password) are
throttled; read-heavy authenticated endpoints are left untouched.

Uses in-memory storage by default (fine for a single backend instance /
Render's default single-worker web service). If the deployment scales to
multiple backend instances behind a load balancer, point slowapi at Redis
via storage_uri instead so limits are shared across instances.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)
