from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.user_schema import UserCreate, UserResponse

# Router agrupa todos los endpoints de usuarios bajo el prefijo /users
# y los etiqueta como "Users" 
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Lista en memoria que simula una base de datos.
# Cada usuario es un diccionario con los campos del modelo.
users = [
    {
        "id": 1,
        "name": "Harold",
        "email": "harold@gmail.com",
        "role": "admin",
        "is_active": True
    },
    {
        "id": 2,
        "name": "Carlos",
        "email": "carlos@gmail.com",
        "role": "support",
        "is_active": True
    },
    {
        "id": 3,
        "name": "Maria",
        "email": "maria@gmail.com",
        "role": "user",
        "is_active": False
    }
]


# Endpoint: GET /users
# Response Model: list[UserResponse]
# Este endpoint devuelve todos los usuarios almacenados en la lista.
# Acepta parámetros de consulta opcionales para filtrar el resultado.
@router.get("", response_model=list[UserResponse])
def get_users(
    # Si el cliente envía /users?role=admin, solo se devuelven los admin.
    # Si no envía el parámetro, role es None y no se filtra por rol.
    role: str | None = Query(default=None),
    # Permite filtrar por estado activo o inactivo.
    # Se usa tipo bool para que FastAPI convierta "true"/"false" automáticamente.
    is_active: bool | None = Query(default=None)
):
    # Empezamos con la lista completa de usuarios.
    result = users
    # Si llegó el parámetro role, filtramos la lista.
    # Este if solo se ejecuta cuando la URL incluye ?role=algun_valor.
    if role is not None:
        result = [
            user for user in result
            if user["role"] == role
        ]

    # Si llegó el parámetro is_active, filtramos por estado.
    # Ejemplos:
    #   /users?is_active=true  -> solo activos
    #   /users?is_active=false -> solo inactivos
    # Se pueden combinar con role: /users?role=admin&is_active=true
    if is_active is not None:
        result = [
            user for user in result
            if user["is_active"] == is_active
        ]

    # FastAPI serializa la lista al JSON de respuesta automáticamente.
    return result


# Endpoint: GET /users/{user_id}
# Path Parameter: user_id va dentro de la URL.
# Ejemplo real: GET /users/1
# Este endpoint busca un usuario específico por su ID.
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # Recorremos la lista buscando el usuario con el ID solicitado.
    for user in users:
        if user["id"] == user_id:
            # Si lo encontramos, lo devolvemos directamente.
            return user

    # Si terminamos el ciclo sin encontrarlo, lanzamos un error 404.
    # HTTPException permite personalizar el código y el mensaje de error.
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )
# Endpoint: POST /users
# Response Model: UserResponse
# Status Code: 201 Created
# Este endpoint crea un usuario nuevo a partir de los datos del body.
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    # Antes de crear el usuario, revisamos si el email ya existe.
    # Esto previene correos duplicados en la lista.
    for existing_user in users:
        if existing_user["email"] == user.email:
            # Si el email está registrado, devolvemos un error 400.
            raise HTTPException(
                status_code=400,
                detail="El correo ya está registrado"
            )
    # Generamos un ID nuevo tomando el ID máximo actual y sumando 1.
    # Como los usuarios de prueba tienen IDs 1, 2 y 3, el nuevo será 4.
    new_id = max(existing_user["id"] for existing_user in users) + 1
    # model_dump() convierte el objeto Pydantic a un diccionario Python.
    # Con ** desempaquetamos ese diccionario dentro del nuevo diccionario
    # y le agregamos el campo "id".
    new_user = {
        "id": new_id,
        **user.model_dump()
    }
    # Agregamos el nuevo usuario a la lista en memoria.
    users.append(new_user)
    # Devolvemos el usuario creado. FastAPI lo serializa usando UserResponse.
    return new_user
