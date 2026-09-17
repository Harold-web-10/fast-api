from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanStatus


class DeviceUnavailableError(Exception):
    pass


class LoanAlreadyReturnedError(Exception):
    pass


class LoanStateConflictError(Exception):
    pass


def get_all_loans(
    db: Session,
    status: LoanStatus | None = None,
    user_email: str | None = None,
    device_type: str | None = None,
    search: str | None = None,
) -> list[Loan]:
    statement = (
        select(Loan)
        .join(Loan.user)
        .join(Loan.device)
        .options(joinedload(Loan.user), joinedload(Loan.device))
    )
    conditions = []

    if status is not None:
        conditions.append(Loan.status == status)

    if user_email is not None:
        conditions.append(User.email.ilike(user_email))

    if device_type is not None:
        conditions.append(Device.device_type == device_type)

    if search:
        search_value = f"%{search}%"
        conditions.append(
            or_(
                User.name.ilike(search_value),
                User.email.ilike(search_value),
                Device.name.ilike(search_value),
                Device.serial_number.ilike(search_value),
                Loan.status.ilike(search_value),
            )
        )

    if conditions:
        statement = statement.where(and_(*conditions))

    statement = statement.order_by(Loan.loan_date.desc(), Loan.id.desc())
    return list(db.scalars(statement).unique().all())


def get_loan_by_id(db: Session, loan_id: int) -> Loan | None:
    statement = (
        select(Loan)
        .where(Loan.id == loan_id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
    )
    return db.scalars(statement).unique().one_or_none()


def get_user_loans(db: Session, user_id: int) -> list[Loan]:
    user = db.get(User, user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    statement = (
        select(Loan)
        .where(Loan.user_id == user_id)
        .options(joinedload(Loan.device))
        .order_by(Loan.loan_date.desc(), Loan.id.desc())
    )
    return list(db.scalars(statement).all())


def get_device_loans(db: Session, device_id: int) -> list[Loan]:
    device = db.get(Device, device_id)
    if device is None:
        raise LookupError("Dispositivo no encontrado")

    statement = (
        select(Loan)
        .where(Loan.device_id == device_id)
        .options(joinedload(Loan.user))
        .order_by(Loan.loan_date.desc(), Loan.id.desc())
    )
    return list(db.scalars(statement).all())


def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
    user = db.get(User, loan_data.user_id)
    if user is None:
        raise LookupError("Usuario no encontrado")

    device = db.get(Device, loan_data.device_id)
    if device is None:
        raise LookupError("Dispositivo no encontrado")

    if not device.is_available:
        raise DeviceUnavailableError("El dispositivo no está disponible")

    loan = Loan(
        user_id=loan_data.user_id,
        device_id=loan_data.device_id,
        loan_date=loan_data.loan_date or datetime.utcnow(),
        status="active",
    )
    device.is_available = False
    db.add(loan)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan_by_id(db, loan_id)
    if loan is None:
        raise LookupError("Préstamo no encontrado")

    if loan.status == "returned":
        raise LoanAlreadyReturnedError("El préstamo ya fue devuelto")

    if loan.status not in ("active", "overdue"):
        raise LoanStateConflictError("El estado del préstamo no permite la devolución")

    loan.status = "returned"
    loan.return_date = datetime.utcnow()
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan
