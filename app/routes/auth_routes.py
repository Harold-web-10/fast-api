import asyncio
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user_schema import Token, TokenData
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    verify_password,
)
from app.services.user_service import get_user_by_email


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description=(
        "Autentica un usuario con correo y contraseña. "
        "Devuelve un access_token JWT para usar como Bearer."
    ),
    response_description="Token de acceso emitido",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Flujo OAuth2PasswordBearer:

    1. Valida que el usuario exista (por email).
    2. Verifica que esté activo.
    3. Comprueba la contraseña con verify_password().
    4. Genera un JWT con sub = user.id.
    """
    user = await asyncio.to_thread(get_user_by_email, db, form_data.username)
    if user is None:
        # No revelamos si el problema fue usuario o contraseña.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=TokenData,
    summary="Consulta el usuario actual",
    description="Devuelve la información del usuario autenticado mediante el Bearer token.",
    response_description="Datos del usuario autenticado",
)
async def read_users_me(current_user=Depends(get_current_user)):
    return {"username": current_user.email, "user_id": current_user.id, "role": current_user.role}