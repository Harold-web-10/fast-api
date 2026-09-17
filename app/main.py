from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.database.connection import Base, engine
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
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
            "description": "Gestión de préstamos, devoluciones, relaciones y filtros avanzados.",
        },
    ],
    lifespan=lifespan,
)


@app.middleware("http")
async def add_app_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    return response


app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)
