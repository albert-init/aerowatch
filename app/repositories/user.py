from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Fetch a user by their email address.
        Critical for authentication and duplicate-check logic.
        """
        result = await db.execute(select(self.model).where(self.model.email == email))

        # one_or_none() prevents silent data corruption by
        # raising an exception if multiple users share the same email.
        return result.scalars().one_or_none()


# Instantiate a singleton to be used across the application
user_repo = UserRepository(User)
