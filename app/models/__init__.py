# app/models/__init__.py

# 1. Import the Base so it is exposed to the Alembic migration context
from app.core.database import Base

# 2. Import all SQLAlchemy models to register them with Base.metadata
from app.models.user import User
from app.models.ticket import WatchTicket, PriceLog

# 3. Import Enums for convenient top-level access (Note: these are not Base models)
from app.models.ticket import TicketStatus, PriorityLevel

# Explicitly declare public exports.
# WARNING: To avoid circular imports, do not import from `app.models`
# inside your application logic. Import directly from the module files instead.
__all__ = [
    "Base",
    "User",
    "WatchTicket",
    "PriceLog",
    "TicketStatus",
    "PriorityLevel",
]
