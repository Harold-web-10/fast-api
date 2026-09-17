from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schema import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services.device_service import (
    DeviceInUseError,
    create_device as service_create_device,
    delete_device as service_delete_device,
    get_all_devices,
    get_device_by_id,
    patch_device as service_patch_device,
    update_device as service_update_device,
)


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Listar dispositivos",
    description="Obtiene dispositivos. Permite filtrar por tipo, disponibilidad, marca y texto de búsqueda.",
    response_description="Lista de dispositivos encontrados",
)
def get_devices(
    device_type: str | None = Query(default=None, description="Filtra por tipo de dispositivo"),
    is_available: bool | None = Query(default=None, description="Filtra por disponibilidad"),
    brand: str | None = Query(default=None, description="Filtra por marca"),
    search: str | None = Query(default=None, description="Busca en nombre, número de serie, marca o tipo"),
    db: Session = Depends(get_db),
):
    return get_all_devices(
        db,
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Obtener dispositivo por ID",
    description="Busca un dispositivo por su identificador único.",
    response_description="Dispositivo encontrado",
)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    device = get_device_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dispositivo",
    description="Registra un nuevo dispositivo en la base de datos.",
    response_description="Dispositivo creado exitosamente",
)
def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
):
    try:
        return service_create_device(db, device)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo completo",
    description="Reemplaza los campos enviados de un dispositivo.",
    response_description="Dispositivo actualizado exitosamente",
)
def replace_device(
    device_id: int,
    device: DeviceUpdate,
    db: Session = Depends(get_db),
):
    updates = device.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar",
        )

    try:
        return service_update_device(db, device_id, device)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar dispositivo parcialmente",
    description="Modifica solo los campos enviados. Los demás se mantienen igual.",
    response_description="Dispositivo actualizado parcialmente",
)
def partial_update_device(
    device_id: int,
    device: DeviceUpdate,
    db: Session = Depends(get_db),
):
    updates = device.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar",
        )

    try:
        return service_patch_device(db, device_id, updates)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dispositivo",
    description="Elimina un dispositivo del sistema por su ID.",
    response_description="Dispositivo eliminado exitosamente",
)
def remove_device(
    device_id: int,
    db: Session = Depends(get_db),
):
    try:
        service_delete_device(db, device_id)
    except DeviceInUseError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado") from exc
