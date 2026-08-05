from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import Settings, settings as default_settings


class Base(DeclarativeBase):
    """Declarative base class for database models."""

    pass


class AuditLog(Base):
    """
    AuditLog table storing trade evaluation history.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reasoning_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


_global_engine: Optional[AsyncEngine] = None


def get_engine(config: Optional[Settings] = None) -> AsyncEngine:
    """Returns or initializes the async SQLAlchemy engine."""
    global _global_engine
    if _global_engine is None or config is not None:
        cfg = config or default_settings
        _global_engine = create_async_engine(cfg.DATABASE_URL, echo=False)
    return _global_engine


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Creates an async sessionmaker bound to the provided engine."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db(engine: Optional[AsyncEngine] = None) -> None:
    """Creates all database tables asynchronously."""
    async_engine = engine or get_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def log_audit_entry(
    symbol: str,
    confidence_score: float,
    is_approved: bool,
    reasoning_summary: str,
    engine: Optional[AsyncEngine] = None,
) -> AuditLog:
    """
    Asynchronously logs a trade evaluation entry into the AuditLog table.

    Args:
        symbol: Stock ticker symbol.
        confidence_score: Confidence score of the proposal.
        is_approved: Safety check approval boolean.
        reasoning_summary: Trade reasoning or safety failure text.
        engine: Optional AsyncEngine instance for dependency injection.

    Returns:
        The created AuditLog instance.
    """
    async_engine = engine or get_engine()
    session_factory = get_session_maker(async_engine)

    audit_entry = AuditLog(
        symbol=symbol,
        confidence_score=confidence_score,
        is_approved=is_approved,
        reasoning_summary=reasoning_summary,
        created_at=datetime.now(timezone.utc),
    )

    async with session_factory() as session:
        async with session.begin():
            session.add(audit_entry)
        await session.refresh(audit_entry)

    return audit_entry
