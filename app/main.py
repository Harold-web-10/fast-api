from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.database.connection import Base, engine
from app.models.user_model import User
from app.routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="device_systems API",
    description="API REST para gestión de usuarios con persistencia en SQLite y SQLAlchemy.",
    version="1.0",
    contact={
        "name": "Aprendiz ADSO",
        "url": "https://sena.edu.co",
    },
    tags_metadata=[
        {
            "name": "Users",
            "description": "Operaciones CRUD sobre usuarios: listar, crear, actualizar y eliminar.",
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
