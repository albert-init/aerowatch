from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import PriceLog
from app.repositories.base import BaseRepository


class PriceLogRepository(BaseRepository[PriceLog]):
    async def get_by_ticket(
        self, db: AsyncSession, ticket_id: int, limit: int = 50
    ) -> Sequence[PriceLog]:
        """Fetch the price history of a specific ticket.

        Orders the logs from newest to oldest so we can cleanly render price
        trends in the UI later. Assumes a composite index exists on
        (ticket_id, created_at DESC) for maximum performance.
        """
        result = await db.execute(
            select(self.model)
            .where(self.model.ticket_id == ticket_id)
            .order_by(self.model.checked_at.desc())
            .limit(limit)
        )

        return result.scalars().all()


# Singleton instance for application-wide use
price_log_repo = PriceLogRepository(PriceLog)
