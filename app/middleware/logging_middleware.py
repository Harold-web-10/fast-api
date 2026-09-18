"""Middleware de registro de solicitudes."""
import time

from fastapi import FastAPI, Request
from fastapi.responses import Response


def register_logging_middleware(app: FastAPI) -> None:
    """
    Registra un middleware HTTP que muestra el ciclo:

        Request -> Middleware -> Endpoint -> Response -> Middleware -> Cliente

    El middleware:
    - Intercepta cada solicitud.
    - Registra el método HTTP y la ruta.
    - Mide el tiempo de procesamiento.
    - Permite continuar la solicitud (call_next).
    - Procesa la respuesta agregando headers de identificación.
    """
    @app.middleware("http")
    async def log_request_middleware(request: Request, call_next):
        method = request.method
        path = request.url.path
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-API-Version"] = "1.0"
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        print(f"[{method}] {path} -> {response.status_code} ({duration_ms:.2f}ms)")
        return response