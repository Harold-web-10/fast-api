from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate, UserRole
from app.services.user_service import (
    SortField,
    SortOrder,
    create_user as service_create_user,
    delete_user as service_delete_user,
    get_all_users,
    patch_user as service_patch_user,
    update_user as service_update_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Obtiene todos los usuarios. Se pueden aplicar filtros por rol y estado, además de ordenamiento.",
    response_description="Lista de usuarios encontrados",
)
def get_users(
    role: UserRole | None = Query(default=None, description="Filtra por rol: admin, support o user"),
    is_active: bool | None = Query(default=None, description="Filtra por estado activo o inactivo"),
    sort_by: SortField = Query(default="created_at", description="Campo por el que se ordenan los usuarios"),
    order: SortOrder = Query(default="asc", description="Sentido del ordenamiento: asc o desc"),
    db: Session = Depends(get_db),
):
    return get_all_users(
        db,
        role=role,
        is_active=is_active,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Busca un usuario por su identificador único.",
    response_description="Usuario encontrado",
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_user_or_404),
):
    return current_user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Registra un nuevo usuario en la base de datos.",
    response_description="Usuario creado exitosamente",
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return service_create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    description="Reemplaza la información de un usuario por los datos enviados.",
    response_description="Usuario actualizado exitosamente",
)
def replace_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_or_404),
):
    updates = user.model_dump(exclude_unset=True, exclude_none=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar",
        )

    try:
        return service_update_user(db, user_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados. Los demás se mantienen igual.",
    response_description="Usuario actualizado parcialmente",
)
def partial_update_user(
    user_id: int,
    user: UserPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_or_404),
):
    updates = user.model_dump(exclude_unset=True, exclude_none=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar",
        )

    try:
        return service_patch_user(db, user_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema por su ID.",
    response_description="Usuario eliminado exitosamente",
)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_or_404),
):
    try:
        service_delete_user(db, user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
