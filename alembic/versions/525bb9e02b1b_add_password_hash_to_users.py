"""add password_hash to users

Revision ID: 525bb9e02b1b
Revises: 8ed67c3531e9
Create Date: 2026-09-17 17:46:17.909181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '525bb9e02b1b'
down_revision: Union[str, Sequence[str], None] = '8ed67c3531e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite no soporta ALTER COLUMN ... SET NOT NULL directamente, por
    # eso usamos batch_alter_table que recrea la tabla internamente.
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(), nullable=True))

    # Rellenar usuarios existentes con un hash por defecto. Deben cambiar
    # su contraseña en el próximo login.
    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id FROM users")).fetchall()
    default_hash = (
        "$2b$12$emZqAw9TftHRe59efJF9vuZaa074iqtRoRIRGTHk15VsN3PEvEMcW"
    )
    for row in users:
        bind.execute(
            sa.text("UPDATE users SET password_hash = :h WHERE id = :id"),
            {"h": default_hash, "id": row[0]},
        )

    # Hacer la columna NOT NULL para futuros registros.
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('password_hash', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('password_hash')