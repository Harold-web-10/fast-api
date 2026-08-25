from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.routes.user_routes import router as user_router

# Creamos la aplicación FastAPI.
# Los metadatos se muestran en la documentación de Swagger y ReDoc.
app = FastAPI(
    title="device_systems API",
    description="API REST para gestión de usuarios. Proyecto desarrollado para la clase de FastAPI intermedio del SENA.",
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
    ]
)


# Middleware HTTP: se ejecuta en cada petición antes de llegar a los endpoints.
# Agrega cabeceras personalizadas a todas las respuestas.
@app.middleware("http")
async def add_app_headers(request: Request, call_next):
    response: Response = await call_next(request)

    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    return response


# Conectamos el router de usuarios a la aplicación principal.
# Todas las rutas de /users quedan disponibles.
app.include_router(user_router)
