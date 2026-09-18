"""Paquete de middlewares del proyecto."""
from app.middleware.auth_middleware import configure_auth_middleware
from app.middleware.cors import configure_cors
from app.middleware.logging_middleware import register_logging_middleware

__all__ = [
    "configure_auth_middleware",
    "configure_cors",
    "register_logging_middleware",
]