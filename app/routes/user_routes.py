from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies.user_dependencies import get_user_or_404
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services.user_service import (
    create_user as service_create_user,
    delete_user as service_delete_user,
    get_all_users,
    patch_user as service_patch_user,
    update_user as service_update_user,
)

# Router agrupa todos los endpoints de usuarios bajo el prefijo /users
# y los etiqueta como "Users" en la documentación de Swagger.
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Endpoint: GET /users
# Response Model: list[UserResponse]
# Devuelve todos los usuarios. Acepta filtros opcionales por rol y estado.
@router.get("", response_model=list[UserResponse], summary="Listar usuarios", description="Obtiene todos los usuarios. Se pueden aplicar filtros por rol y estado.", response_description="Lista de usuarios encontrados")
def get_users(
    role: str | None = Query(default=None, description="Filtra por rol: admin, support o user"),
    is_active: bool | None = Query(default=None, description="Filtra por estado activo o inactivo")
):
    return get_all_users(role=role, is_active=is_active)


# Endpoint: GET /users/{user_id}
# Path Parameter: user_id dentro de la URL.
# Devuelve un usuario específico por su ID.
@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID", description="Busca un usuario por su identificador único.", response_description="Usuario encontrado")
def get_user(user_id: int):
    # Usamos la dependencia para buscar el usuario o lanzar 404 automáticamente.
    return get_user_or_404(user_id)


# Endpoint: POST /users
# Response Model: UserResponse
# Crea un usuario nuevo validando los datos y evitando correos duplicados.
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear usuario", description="Registra un nuevo usuario en el sistema.", response_description="Usuario creado exitosamente")
def create_user(user: UserCreate):
    try:
        # Llamamos al servicio para crear el usuario.
        return service_create_user(user)
    except ValueError as e:
        # Si el servicio detecta correo duplicado, devolvemos 400.
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint: PUT /users/{user_id}
# Response Model: UserResponse
# Reemplaza completamente los datos de un usuario existente.
@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario completo", description="Reemplaza toda la información de un usuario por nuevos datos.", response_description="Usuario actualizado exitosamente")
def replace_user(user_id: int, user: UserUpdate):
    # Verificamos que el usuario exista antes de continuar.
    get_user_or_404(user_id)

    # PUT requiere que al menos un campo sea enviado.
    # Si el cliente envía un objeto vacío, no tiene sentido actualizar.
    if user.model_dump(exclude_none=True) == {}:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar"
        )

    try:
        return service_update_user(user_id, user)
    except ValueError as e:
        # Error de correo duplicado.
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError:
        # Si el usuario desapareció entre la validación y la actualización.
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Endpoint: PATCH /users/{user_id}
# Response Model: UserResponse
# Actualiza solo los campos enviados, sin modificar los demás.
@router.patch("/{user_id}", response_model=UserResponse, summary="Actualizar usuario parcialmente", description="Modifica solo los campos enviados. Los demás se mantienen igual.", response_description="Usuario actualizado parcialmente")
def partial_update_user(user_id: int, user: UserPatch):
    # Verificamos que el usuario exista.
    get_user_or_404(user_id)

    # Extraemos solo los campos que el cliente envió (los que no son None).
    updates = user.model_dump(exclude_none=True)

    # Si no envía ningún campo, devolvemos 400.
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar"
        )

    try:
        return service_patch_user(user_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


# Endpoint: DELETE /users/{user_id}
# Status Code: 204 No Content
# Elimina un usuario existente. No devuelve contenido en la respuesta.
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario", description="Elimina un usuario del sistema por su ID.", response_description="Usuario eliminado exitosamente")
def remove_user(user_id: int):
    # Verificamos que el usuario exista antes de intentar eliminarlo.
    get_user_or_404(user_id)

    try:
        service_delete_user(user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # DELETE exitoso sin contenido en la respuesta.
