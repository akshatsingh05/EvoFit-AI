"""
Adds standard security response headers.

Implemented as a plain ASGI middleware (not Starlette's BaseHTTPMiddleware).
BaseHTTPMiddleware runs the downstream app in a separate task and re-raises
any exception that occurred there after the response has already been sent
by an exception handler further down the stack -- this doesn't change what
the client receives, but it double-logs every handled error as a spurious
second "Exception in ASGI application" traceback, and under real network
conditions (not localhost) has been known to cause the response stream to
be torn down before it's fully flushed. A pure ASGI middleware that only
wraps `send` avoids all of this.
"""
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

_STATIC_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"geolocation=(), microphone=(), camera=()"),
]


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.extend(_STATIC_HEADERS)
                if settings.is_production:
                    headers.append((b"strict-transport-security", b"max-age=63072000; includeSubDomains"))
            await send(message)

        await self.app(scope, receive, send_with_headers)
