from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceInUseError(Exception):
    pass


def get_all_devices(
    db: Session,
    device_type: str | None = None,
    is_available: bool | None = None,
    brand: str | None = None,
    search: str | None = None,
) -> list[Device]:
    statement = select(Device)

    if device_type is not None:
        statement = statement.where(Device.device_type == device_type)

    if is_available is not None:
        statement = statement.where(Device.is_available == is_available)

    if brand is not None:
        statement = statement.where(Device.brand == brand)

    if search:
        search_value = f"%{search}%"
        statement = statement.where(
            or_(
                Device.name.ilike(search_value),
                Device.serial_number.ilike(search_value),
                Device.brand.ilike(search_value),
                Device.device_type.ilike(search_value),
            )
        )

    return list(db.scalars(statement.order_by(Device.id.asc())).all())


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return db.get(Device, device_id)


def get_device_by_serial(db: Session, serial_number: str) -> Device | None:
    statement = select(Device).where(Device.serial_number == serial_number)
    return db.scalar(statement)


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    serial_number = device_data.serial_number.strip()

    if get_device_by_serial(db, serial_number) is not None:
        raise ValueError("El número de serie ya está registrado")

    device = Device(
        name=device_data.name,
        serial_number=serial_number,
        device_type=device_data.device_type,
        brand=device_data.brand,
    )
    db.add(device)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El número de serie ya está registrado") from exc

    db.refresh(device)
    return device


def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device:
    device = get_device_by_id(db, device_id)
    if device is None:
        raise LookupError("Dispositivo no encontrado")

    updates = device_data.model_dump(exclude_unset=True, exclude_none=True)
    serial_number = updates.get("serial_number")

    if serial_number is not None and get_device_by_serial(db, str(serial_number).strip()) is not None:
        if get_device_by_serial(db, str(serial_number).strip()).id != device_id:
            raise ValueError("El número de serie ya está registrado")

    for field, value in updates.items():
        if field == "serial_number":
            value = str(value).strip()
        setattr(device, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El número de serie ya está registrado") from exc

    db.refresh(device)
    return device


def patch_device(db: Session, device_id: int, updates: dict) -> Device:
    device = get_device_by_id(db, device_id)
    if device is None:
        raise LookupError("Dispositivo no encontrado")

    serial_number = updates.get("serial_number")
    if serial_number is not None:
        serial_number = str(serial_number).strip()
        existing_device = get_device_by_serial(db, serial_number)
        if existing_device is not None and existing_device.id != device_id:
            raise ValueError("El número de serie ya está registrado")

    for field, value in updates.items():
        if field == "serial_number":
            value = str(value).strip()
        setattr(device, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("El número de serie ya está registrado") from exc

    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> None:
    device = get_device_by_id(db, device_id)
    if device is None:
        raise LookupError("Dispositivo no encontrado")

    if db.scalar(select(Loan.id).where(Loan.device_id == device_id).limit(1)) is not None:
        raise DeviceInUseError("El dispositivo tiene préstamos registrados")

    db.delete(device)
    db.commit()
