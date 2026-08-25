from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


# Esquema para crear un usuario (POST).
# Todos los campos son obligatorios excepto is_active que tiene valor por defecto.
class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool = True


# Esquema para actualizar un usuario completo (PUT).
# Todos los campos son opcionales porque el cliente puede enviar solo los que quiera cambiar.
# Sin embargo, PUT debe recibir todos los datos del usuario, así que en la ruta
# validaremos que al menos vengan los campos necesarios.
class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None


# Esquema para actualizar parcialmente un usuario (PATCH).
# Todos los campos son opcionales. El cliente envía solo los que desea modificar.
class UserPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None


# Esquema de respuesta. Hereda de UserCreate y agrega id.
# Se usa para definir la estructura de los datos que la API devuelve.
class UserResponse(UserCreate):
    id: int
