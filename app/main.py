from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.routes.user_routes import router as user_router

# Creamos la aplicación FastAPI con título y versión.
# Estos datos se muestran en la documentación de Swagger.
app = FastAPI(
    title="device_systems API",
    version="1.0"
)


# Middleware HTTP: se ejecuta en cada petición antes de llegar a los endpoints.
# Su función es agregar cabeceras personalizadas a todas las respuestas.
@app.middleware("http")
async def add_app_headers(request: Request, call_next):
    # call_next ejecuta el resto de la aplicación (rutas, otros middlewares, etc.)
    response: Response = await call_next(request)

    # Agregamos dos cabeceras personalizadas a la respuesta.
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    return response


# Conectamos el router de usuarios a la aplicación principal.
# Esto hace que todas las rutas definidas en user_routes.py
# queden disponibles bajo el prefijo /users.
app.include_router(user_router)
