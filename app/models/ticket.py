import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class TicketStatus(str, enum.Enum):
    MONITORING = "Monitoring"
    APPROACHING = "Approaching"
    MATCHED = "Matched"


class PriorityLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class WatchTicket(Base):
    __tablename__ = "watch_tickets"

    # Removed index=True to prevent duplicate primary key indexing
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    origin_iata: Mapped[str] = mapped_column(String(3), index=True, nullable=False)
    destination_iata: Mapped[str] = mapped_column(String(3), index=True, nullable=False)
    departure_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    departure_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Added native_enum=False to prevent future Alembic migration crashes
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, native_enum=False, length=50), 
        default=TicketStatus.MONITORING, 
        index=True, 
        nullable=False
    )
    priority: Mapped[PriorityLevel] = mapped_column(
        SQLEnum(PriorityLevel, native_enum=False, length=50), 
        default=PriorityLevel.MEDIUM, 
        nullable=False
    )
    
    # Applied func.now() for database-level time synchronization
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    ticket_owner: Mapped["User"] = relationship(back_populates="user_watch_tickets")

    # Added passive_deletes=True to prevent SQLAlchemy from RAM-loading records during deletion
    ticket_price_logs: Mapped[list["PriceLog"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", passive_deletes=True
    )


class PriceLog(Base):
    __tablename__ = "price_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("watch_tickets.id", ondelete="CASCADE"), index=True, nullable=False
    )

    price_found: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    ticket: Mapped["WatchTicket"] = relationship(back_populates="ticket_price_logs")
