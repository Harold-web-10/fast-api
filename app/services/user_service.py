from typing import Literal

from app.data.users_db import users
from app.schemas.user_schema import UserCreate, UserResponse


# Servicio: contiene la lógica de negocio de los usuarios.
# Las rutas delegan aquí las operaciones para mantener el código organizado.
# Si en el futuro cambiamos a base de datos, solo se modifica este archivo.


def get_all_users(role: str | None = None, is_active: bool | None = None):
    # Devuelve todos los usuarios, con filtros opcionales.
    result = users

    if role is not None:
        result = [user for user in result if user["role"] == role]

    if is_active is not None:
        result = [user for user in result if user["is_active"] == is_active]

    return result


def get_user_by_id(user_id: int):
    # Busca un usuario por ID. Si no lo encuentra, devuelve None.
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def create_user(user_data: UserCreate):
    # Crea un usuario nuevo después de validar el correo duplicado.
    for existing_user in users:
        if existing_user["email"] == user_data.email:
            raise ValueError("El correo ya está registrado")

    new_id = max((u["id"] for u in users), default=0) + 1
    new_user = {
        "id": new_id,
        **user_data.model_dump()
    }
    users.append(new_user)
    return new_user


def update_user(user_id: int, user_data: UserCreate):
    # Reemplaza completamente los datos de un usuario existente.
    user = get_user_by_id(user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    # Verificamos correo duplicado, ignorando el propio usuario actual.
    for existing_user in users:
        if existing_user["email"] == user_data.email and existing_user["id"] != user_id:
            raise ValueError("El correo ya está registrado")

    user.update(user_data.model_dump())
    return user


def patch_user(user_id: int, updates: dict):
    # Actualiza solo los campos enviados en el diccionario.
    user = get_user_by_id(user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    if not updates:
        raise ValueError("No se enviaron datos para actualizar")

    # Verificamos correo duplicado si viene en la actualización.
    if "email" in updates:
        for existing_user in users:
            if existing_user["email"] == updates["email"] and existing_user["id"] != user_id:
                raise ValueError("El correo ya está registrado")

    user.update(updates)
    return user


def delete_user(user_id: int):
    # Elimina un usuario por ID.
    user = get_user_by_id(user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    users.remove(user)
