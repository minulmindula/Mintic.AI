from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global risk parameters and application settings for Mintic.AI."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ALLOWED_SYMBOLS: set[str] = Field(
        default={"AAPL", "GOOGL", "MSFT", "NVDA", "AMZN", "TSLA", "META", "SPY"},
        description="Allowed whitelist of tradeable stock market symbols",
    )
    MAX_POSITION_SIZE_GBP: float = Field(
        default=10000.0,
        gt=0,
        description="Maximum allowed position size in GBP",
    )
    MIN_CONFIDENCE_THRESHOLD: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score required to approve a trade proposal (0.0 to 1.0)",
    )
    MAX_DAILY_DRAWDOWN_PERCENT: float = Field(
        default=5.0,
        ge=0.0,
        le=100.0,
        description="Maximum allowed daily drawdown percentage",
    )

    ALPACA_API_KEY: str = Field(
        default="PKTEST_KEY_ID",
        description="Alpaca API Key ID for paper trading",
    )
    ALPACA_SECRET_KEY: str = Field(
        default="PKTEST_SECRET_KEY",
        description="Alpaca Secret Key for paper trading",
    )
    ALPACA_PAPER: bool = Field(
        default=True,
        description="Enforce Alpaca paper trading mode",
    )

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./mintic_audit.db",
        description="Async database connection string for audit logging",
    )
    QDRANT_LOCATION: str = Field(
        default=":memory:",
        description="Qdrant vector store location or host",
    )


settings: Settings = Settings()
