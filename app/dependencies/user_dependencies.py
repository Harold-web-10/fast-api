from fastapi import Depends, HTTPException

from app.services.user_service import get_user_by_id


# Dependencia: get_user_or_404
# Esta función se puede usar en cualquier ruta que necesite un usuario por ID.
# Si el usuario existe, lo devuelve. Si no, lanza un error 404.
# Así no repetimos la misma lógica de búsqueda en cada endpoint.
def get_user_or_404(user_id: int):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    return user
