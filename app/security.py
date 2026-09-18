"""
Módulo de seguridad: hashing de contraseñas, JWT, OAuth2PasswordBearer
y dependencias de autenticación/autorización.

Todas las funciones están pensadas para ser reutilizadas mediante
``Depends()`` en los routers.
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user_model import User

# ---------------------------------------------------------------------------
# Configuración (variables de entorno con valores por defecto seguros para
# desarrollo académico). En producción deben sobre escribirse.
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "device_systems_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ---------------------------------------------------------------------------
# Hashing de contraseñas (bcrypt a través de passlib)
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincida con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# OAuth2PasswordBearer
#
# auto_error=False porque la validación real del token la hace el AuthMiddleware
# en la pila de middlewares. Esta variable se usa SOLO para que Swagger muestre
# el botón Authorize y documente el esquema de seguridad.
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scheme_name="OAuth2PasswordBearer",
    description=(
        "Envía el token Bearer obtenido en POST /auth/login. "
        "Ejemplo: Authorization: Bearer <token>"
    ),
    auto_error=False,
)

# Esquema de seguridad para Swagger/OpenAPI.
security_schemes = {
    "OAuth2PasswordBearer": {
        "type": "oauth2",
        "flows": {
            "password": {
                "tokenUrl": "auth/login",
                "scopes": {},
            }
        },
    }
}


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT firmado con HS256.

    ``data`` debe contener al menos ``sub`` (id del usuario). Se añade
    ``exp`` automáticamente.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un JWT. Devuelve el payload o None si es inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Dependencias de autenticación (async para usar en endpoints async def)
# ---------------------------------------------------------------------------
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Valida el Bearer token, obtiene el user_id y busca el User activo.

    Errores:
        401 -> token ausente, inválido o expirado
        401 -> usuario no existe
        401 -> usuario inactivo
    """
    # El AuthMiddleware ya validó el JWT y dejó el payload en request.state.
    payload = getattr(request.state, "auth_payload", None)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # La consulta a BD se ejecuta en un thread para no bloquear el event loop.
    user = await asyncio.to_thread(db.get, User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ---------------------------------------------------------------------------
# Dependencias de autorización por rol
# ---------------------------------------------------------------------------
def require_role(required_role: str):
    """
    Factory que crea una dependencia para verificar rol.

    Uso:
        @router.post("/admin", dependencies=[Depends(require_role("admin"))])
    """

    async def role_dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return current_user

    return role_dependency