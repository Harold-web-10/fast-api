from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserUpdate
from app.security import hash_password


class UserInUseError(Exception):
    pass


SortField = Literal["name", "created_at"]
SortOrder = Literal["asc", "desc"]


def get_all_users(
    db: Session,
    role: str | None = None,
    is_active: bool | None = None,
    sort_by: SortField = "created_at",
    order: SortOrder = "asc",
) -> list[User]:
    statement = select(User)

    if role is not None:
        statement = statement.where(User.role == role)

    if is_active is not None:
        statement = statement.where(User.is_active == is_active)

    sort_column = User.name if sort_by == "name" else User.created_at
    sort_operation = sort_column.asc() if order == "asc" else sort_column.desc()
    statement = statement.order_by(sort_operation, User.id.asc())

    return list(db.scalars(statement).all())


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str, exclude_id: int | None = None) -> User | None:
    statement = select(User).where(User.email == email)
    if exclude_id is not None:
        statement = statement.where(User.id != exclude_id)
    return db.scalar(statement)


def create_user(db: Session, user_data: UserCreate) -> User:
    email = str(user_data.email)

    if get_user_by_email(db, email) is not None:
        raise ValueError("El correo ya está registrado")

    user = User(
        name=user_data.name,
        email=email,
        role=user_data.role,
        is_active=user_data.is_active,
        # La contraseña se almacena hasheada, nunca en texto plano.
        password_hash=hash_password(user_data.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El correo ya está registrado") from exc

    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    updates = user_data.model_dump(exclude_unset=True, exclude_none=True)
    email = updates.get("email")

    if email is not None and get_user_by_email(db, str(email), exclude_id=user_id) is not None:
        raise ValueError("El correo ya está registrado")

    # Si se envía una nueva contraseña, hay que hashearla.
    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El correo ya está registrado") from exc

    db.refresh(user)
    return user


def patch_user(db: Session, user_id: int, updates: dict) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    if not updates:
        raise ValueError("No se enviaron datos para actualizar")

    email = updates.get("email")
    if email is not None and get_user_by_email(db, str(email), exclude_id=user_id) is not None:
        raise ValueError("El correo ya está registrado")

    # Si se envía una nueva contraseña, hay que hashearla.
    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El correo ya está registrado") from exc

    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    if db.scalar(select(Loan.id).where(Loan.user_id == user_id).limit(1)) is not None:
        raise UserInUseError("El usuario tiene préstamos registrados")

    db.delete(user)
    db.commit()