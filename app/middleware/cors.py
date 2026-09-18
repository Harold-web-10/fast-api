"""Configuración del middleware CORS."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI) -> None:
    """
    Permite que un frontend (puerto distinto) consuma la API.

    CORS (Cross-Origin Resource Sharing) es el protocolo que el navegador
    usa para autorizar peticiones entre orígenes distintos. Sin él, el
    navegador bloquea las peticiones de un frontend a la API.

    Se permite:
    - Cualquier origen (allow_origins=["*"]). En producción conviene
      restringirlo a los orígenes conocidos.
    - Los métodos HTTP: GET, POST, PUT, PATCH, DELETE, OPTIONS.
    - El header Authorization (para enviar Bearer TOKEN) y Content-Type.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )