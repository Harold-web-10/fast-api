"""Dependencia asíncrona de base de datos.

Devuelve una Session de SQLAlchemy para usarla en endpoints ``async def``.
Las operaciones de BD se ejecutan en un thread pool mediante
``asyncio.to_thread`` para no bloquear el event loop.
"""
import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal


async def get_async_db() -> AsyncGenerator[Session, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        # Cierre en un thread para no bloquear.
        await asyncio.to_thread(db.close)