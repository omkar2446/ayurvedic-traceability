"""Initialize the migration history without domain tables.

Revision ID: 0001_phase1
Revises:
Create Date: 2026-08-26
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001_phase1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
