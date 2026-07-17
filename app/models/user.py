import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ticket import WatchTicket


class User(Base):
    __tablename__ = "users"

    # Removed index=True because primary_key=True already creates the index.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Enforces unique email constraints at the database level
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Swapped to server_default so the database generates the time, preventing clock drift.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Combined server_default and onupdate for perfect database-level time tracking.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Cleaned up typing to use standard lowercase 'list'
    user_watch_tickets: Mapped[list["WatchTicket"]] = relationship(
        back_populates="ticket_owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
