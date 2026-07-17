from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ticket import WatchTicket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[WatchTicket]):
    async def get_active_tickets(self, db: AsyncSession) -> Sequence[WatchTicket]:
        """Fetch all active watch tickets.

        This is the exact query our background Celery worker will run to
        determine which items need live price checks.
        """
        result = await db.execute(
            select(self.model)
            # Idiomatic boolean check
            .where(self.model.is_active)
            # Eagerly loads the user relationship to prevent async greenlet errors in Celery
            .options(selectinload(self.model.user))
        )

        return result.scalars().all()

    async def get_by_user(
        self, db: AsyncSession, user_id: int
    ) -> Sequence[WatchTicket]:
        """Fetch all tracking tickets belonging to a specific user."""
        result = await db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )

        return result.scalars().all()


# Singleton instance for application-wide use
ticket_repo = TicketRepository(WatchTicket)
