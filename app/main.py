from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.database.connection import Base, engine
from app.middleware import (
    configure_auth_middleware,
    configure_cors,
    register_logging_middleware,
)
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.routes.auth_routes import router as auth_router
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="device_systems API",
    description="API REST para gestión de usuarios, dispositivos y préstamos con persistencia en SQLite y SQLAlchemy.",
    version="1.0",
    contact={
        "name": "Aprendiz ADSO",
        "url": "https://sena.edu.co",
    },
    openapi_tags=[
        {
            "name": "Users",
            "description": "Operaciones CRUD sobre usuarios: listar, crear, actualizar y eliminar.",
        },
        {
            "name": "Devices",
            "description": "Operaciones CRUD y consultas de dispositivos disponibles.",
        },
        {
            "name": "Loans",
            "description": "Gestión de préstamo, devoluciones, relaciones y filtros avanzados.",
        },
        {
            "name": "Auth",
            "description": "Autenticación con JWT y OAuth2PasswordBearer.",
        },
    ],
    lifespan=lifespan,
    # Respuesta optimizada con ORJSON (más rápida que JSONResponse estándar).
    default_response_class=ORJSONResponse,
)


# ---------------------------------------------------------------------------
# Pila de middlewares (orden de ejecución, de externo a interno):
#
#   Petición:  ServerErrorMiddleware -> CORSMiddleware -> AuthMiddleware
#              -> LoggingMiddleware -> Router -> Endpoint
#   Respuesta: Router -> Endpoint -> LoggingMiddleware -> AuthMiddleware
#              -> CORSMiddleware -> ServerErrorMiddleware -> Cliente
#
# ServerErrorMiddleware es el que Starlette inserta automáticamente como
# el más externo (manejo global de excepciones).
# ---------------------------------------------------------------------------
# CORS: permite que un frontend de otro origen consuma la API.
configure_cors(app)

# Auth: autenticación/autorización vía JWT en la pila de middlewares.
configure_auth_middleware(app)

# Logging: registra método, ruta, tiempo de respuesta y agrega headers.
register_logging_middleware(app)


app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)
app.include_router(auth_router)