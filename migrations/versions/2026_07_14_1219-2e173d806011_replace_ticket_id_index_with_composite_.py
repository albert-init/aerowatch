"""replace ticket_id index with composite index on ticket_id and checked_at

Revision ID: 2e173d806011
Revises: c86405d6ebfd
Create Date: 2026-07-14 12:19:49.681191

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e173d806011"
down_revision: str | Sequence[str] | None = "c86405d6ebfd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_price_logs_ticket_id_checked_at",
        "price_logs",
        ["ticket_id", sa.literal_column("checked_at DESC")],
        unique=False,
    )
    op.drop_index(op.f("ix_price_logs_ticket_id"), table_name="price_logs")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(
        op.f("ix_price_logs_ticket_id"), "price_logs", ["ticket_id"], unique=False
    )
    op.drop_index("ix_price_logs_ticket_id_checked_at", table_name="price_logs")
