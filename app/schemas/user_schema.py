from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# Modelo que define los datos que el cliente envía al crear un usuario.
# FastAPI usará este esquema para validar automáticamente la información
# que llegue en el body de una petición POST.
class UserCreate(BaseModel):
    # name es obligatorio y debe tener mínimo 3 caracteres.
    # Si el cliente envía menos, FastAPI devuelve un error 422.
    name: str = Field(min_length=3)

    # email debe tener formato de correo válido.
    # EmailStr viene de email-validator y revisa que tenga @ y dominio.
    email: EmailStr

    # role solo puede ser uno de estos tres valores literales.
    # Cualquier otro valor causa un error de validación 422.
    role: Literal["admin", "support", "user"]

    # is_active debe ser un valor booleano: true o false.
    # No se aceptan strings como "true" ni números.
    is_active: bool


# Modelo de respuesta que hereda de UserCreate y agrega el id.
# Se usa para definir exactamente qué campos se devuelven al cliente,
# evitando exponer datos internos o campos no autorizados.
class UserResponse(UserCreate):
    id: int
