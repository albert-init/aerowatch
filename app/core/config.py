from functools import cache
from pydantic import SecretStr, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

class Settings(BaseSettings):
    # Database configuration
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # External APIs and Services
    SERPAPI_KEY: SecretStr
    
    # Use RedisDsn to automatically validate format and mask passwords in logs
    REDIS_URL: RedisDsn

    # Pydantic V2 config dict
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def ASYNC_DATABASE_URL(self) -> URL:
        """
        Used by FastAPI and aiomysql for standard async operations.
        Note: Removed @computed_field to prevent Pydantic serialization errors,
        as sqlalchemy.URL is not natively JSON-serializable.
        """
        return URL.create(
            drivername="mysql+aiomysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    @property
    def SYNC_DATABASE_URL(self) -> URL:
        """Used exclusively by Alembic (pymysql) for synchronous schema migrations."""
        return URL.create(
            drivername="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

@cache
def get_settings() -> Settings:
    """
    Cached function to ensure the .env file is read and parsed only once.
    Uses Python 3.9+ @cache which is slightly faster than @lru_cache for unbounded caching.
    """
    return Settings()

# DO NOT instantiate `settings = get_settings()` at the module level.
# Instead, call `get_settings()` inside your application lifespan, 
# or use FastAPI dependency injection: `Depends(get_settings)`.
