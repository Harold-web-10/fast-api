"""Middleware de autenticación y autorización.

Se ejecuta en la pila de middlewares AFTER CORSMiddleware y BEFORE el router.
Flujo:

    ServerErrorMiddleware -> CORSMiddleware -> AuthMiddleware -> Router

El middleware:
- Permite peticiones OPTIONS (preflight CORS).
- Permite POST /auth/login sin autenticación.
- Permite métodos GET (consultas) sin autenticación, como en el diseño original.
- Para POST/PUT/PATCH/DELETE exige un Bearer token JWT válido.
- Adjunta la información del payload a ``request.state.auth_payload``.
- Añade cabeceras personalizadas a la respuesta saliente.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.security import decode_access_token

logger = logging.getLogger("device_systems.auth")

# Métodos HTTP que requieren autenticación.
AUTH_REQUIRED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuthMiddleware:
    """Middleware de autenticación JWT integrado en la pila."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        # Preflight CORS.
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Login público.
        if request.url.path == "/auth/login" and request.method == "POST":
            await self.app(scope, receive, send)
            return

        # Las consultas (GET) son públicas en este proyecto.
        if request.method not in AUTH_REQUIRED_METHODS:
            await self.app(scope, receive, send)
            return

        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            response = JSONResponse(
                {"detail": "No se proporcionó token de acceso"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        payload = decode_access_token(token)
        if payload is None or "sub" not in payload:
            response = JSONResponse(
                {"detail": "Token inválido o expirado"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        try:
            user_id = int(payload["sub"])
        except (TypeError, ValueError):
            response = JSONResponse(
                {"detail": "Token inválido"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        # Adjuntamos la información del payload al request state para que
        # los endpoints y dependencias puedan usarla.
        request.state.auth_payload = payload
        request.state.auth_user_id = user_id

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-authenticated", b"true"))
            await send(message)

        await self.app(scope, receive, send_with_headers)


def configure_auth_middleware(app: FastAPI) -> None:
    """Añade el AuthMiddleware a la aplicación FastAPI."""
    app.add_middleware(AuthMiddleware)