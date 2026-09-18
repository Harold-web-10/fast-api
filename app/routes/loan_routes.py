import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Security, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.security import get_current_user, oauth2_scheme
from app.services.loan_service import (
    DeviceUnavailableError,
    LoanAlreadyReturnedError,
    LoanStateConflictError,
    create_loan as service_create_loan,
    get_all_loans,
    get_device_loans,
    get_loan_by_id,
    get_user_loans,
    return_loan as service_return_loan,
)


router = APIRouter(tags=["Loans"])


@router.get(
    "/loans/details",
    response_model=list[LoanDetailResponse],
    summary="Listar préstamo detallados",
    description="Obtiene préstamo con la información básica del usuario y del dispositivo asociado.",
    response_description="Lista de préstamo detallados",
)
async def get_loan_details(
    db: Session = Depends(get_db),
):
    return await asyncio.to_thread(get_all_loans, db)


@router.get(
    "/loans",
    response_model=list[LoanResponse],
    summary="Listar préstamo",
    description="Obtiene préstamo. Permite filtrar por estado, correo del usuario, tipo de dispositivo y texto de búsqueda.",
    response_description="Lista de préstamo encontrados",
)
async def get_loans(
    status: LoanStatus | None = Query(default=None, description="Filtra por estado: active, returned u overdue"),
    user_email: str | None = Query(default=None, description="Filtra por correo del usuario"),
    device_type: str | None = Query(default=None, description="Filtra por tipo de dispositivo"),
    search: str | None = Query(default=None, description="Busca en usuarios, dispositivos o estado"),
    db: Session = Depends(get_db),
):
    return await asyncio.to_thread(
        get_all_loans,
        db,
        status=status,
        user_email=user_email,
        device_type=device_type,
        search=search,
    )


@router.get(
    "/loans/{loan_id}",
    response_model=LoanResponse,
    summary="Obtener préstamo por ID",
    description="Busca un préstamo por su identificador único.",
    response_description="Préstamo encontrado",
)
async def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
):
    loan = await asyncio.to_thread(get_loan_by_id, db, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan


@router.post(
    "/loans",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Creación de préstamo",
    description="Registra un préstamo cuando el usuario y el dispositivo existen y el dispositivo está disponible. Requiere autenticación.",
    response_description="Préstamo creado exitosamente",
)
async def create_loan(
    request: Request,
    loan: LoanCreate,
    db: Session = Depends(get_db),
    _: str = Security(oauth2_scheme),
):
    try:
        return await asyncio.to_thread(service_create_loan, db, loan)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DeviceUnavailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch(
    "/loans/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver préstamo",
    description="Marca un préstamo como devuelto, registra la fecha y devuelve la disponibilidad del dispositivo. Requiere autenticación.",
    response_description="Préstamo devuelto exitosamente",
)
async def return_loan(
    request: Request,
    loan_id: int,
    db: Session = Depends(get_db),
    _: str = Security(oauth2_scheme),
):
    try:
        return await asyncio.to_thread(service_return_loan, db, loan_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LoanAlreadyReturnedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LoanStateConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get(
    "/users/{user_id}/loans",
    response_model=list[LoanResponse],
    summary="Listar préstamo de un usuario",
    description="Obtiene el historial de préstamo asociado a un usuario.",
    response_description="Historial de préstamo del usuario",
)
async def get_user_loan_history(
    user_id: int,
    db: Session = Depends(get_db),
):
    try:
        return await asyncio.to_thread(get_user_loans, db, user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/devices/{device_id}/loans",
    response_model=list[LoanResponse],
    summary="Listar préstamo de un dispositivo",
    description="Obtiene el historial de préstamo asociado a un dispositivo.",
    response_description="Historial de dispositivo del dispositivo",
)
async def get_device_loan_history(
    device_id: int,
    db: Session = Depends(get_db),
):
    try:
        return await asyncio.to_thread(get_device_loans, db, device_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc