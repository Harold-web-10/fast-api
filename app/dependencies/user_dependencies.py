"""Dependencia para obtener un usuario por ID o fallar con 404."""
import asyncio

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services.user_service import get_user_by_id


async def get_user_or_404(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    user = await asyncio.to_thread(get_user_by_id, db, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )
    return user