"""
SK AgentCorp — Shared Memory (Consensus Memory)

A persistent shared memory store that all agents within a company can read/write.
Implements a key-value store with versioning and conflict resolution.
Used for cross-agent knowledge sharing and consensus building.
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

logger = logging.getLogger(__name__)


class SharedMemoryEntry(Base):
    """A single key-value entry in shared memory."""

    __tablename__ = "shared_memory"

    key: Mapped[str] = mapped_column(String(500), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
    value_type: Mapped[str] = mapped_column(String(20), default="text")  # text | json | list
    written_by_agent_id: Mapped[str] = mapped_column(String(36), default="")
    written_by_agent_name: Mapped[str] = mapped_column(String(255), default="system")
    version: Mapped[int] = mapped_column(default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class SharedMemory:
    """
    Consensus shared memory interface.

    Enables agents to share knowledge, decisions, and state across the company.
    Supports atomic read/write operations with versioning.
    """

    def __init__(self, db: AsyncSession, company_id: str):
        self.db = db
        self.company_id = company_id

    async def get(self, key: str) -> str | None:
        """Read a value from shared memory."""
        entry = await self.db.get(SharedMemoryEntry, (key, self.company_id))
        return entry.value if entry else None

    async def get_json(self, key: str) -> dict | list | None:
        """Read a JSON value from shared memory."""
        raw = await self.get(key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        return None

    async def set(
        self,
        key: str,
        value: str,
        agent_id: str = "",
        agent_name: str = "system",
        value_type: str = "text",
    ) -> None:
        """Write a value to shared memory (upsert)."""
        entry = await self.db.get(SharedMemoryEntry, (key, self.company_id))
        if entry:
            entry.value = value
            entry.value_type = value_type
            entry.written_by_agent_id = agent_id
            entry.written_by_agent_name = agent_name
            entry.version += 1
            entry.updated_at = datetime.now(timezone.utc)
        else:
            entry = SharedMemoryEntry(
                key=key,
                company_id=self.company_id,
                value=value,
                value_type=value_type,
                written_by_agent_id=agent_id,
                written_by_agent_name=agent_name,
            )
            self.db.add(entry)
        await self.db.flush()
        logger.debug(f"SharedMemory [{self.company_id}] set: {key}")

    async def set_json(
        self, key: str, value: dict | list, agent_id: str = "", agent_name: str = "system"
    ) -> None:
        """Write a JSON value to shared memory."""
        await self.set(key, json.dumps(value), agent_id, agent_name, "json")

    async def append_list(
        self, key: str, item: str, agent_id: str = "", agent_name: str = "system"
    ) -> None:
        """Append an item to a list in shared memory."""
        existing = await self.get_json(key)
        if isinstance(existing, list):
            existing.append(item)
        else:
            existing = [item]
        await self.set_json(key, existing, agent_id, agent_name)

    async def delete(self, key: str) -> None:
        """Remove a key from shared memory."""
        entry = await self.db.get(SharedMemoryEntry, (key, self.company_id))
        if entry:
            await self.db.delete(entry)
            await self.db.flush()

    async def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys in shared memory, optionally filtered by prefix."""
        stmt = select(SharedMemoryEntry.key).where(
            SharedMemoryEntry.company_id == self.company_id
        )
        if prefix:
            stmt = stmt.where(SharedMemoryEntry.key.startswith(prefix))
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_all(self) -> dict[str, str]:
        """Dump all shared memory as a dict."""
        stmt = select(SharedMemoryEntry).where(
            SharedMemoryEntry.company_id == self.company_id
        )
        result = await self.db.execute(stmt)
        entries = result.scalars().all()
        return {e.key: e.value for e in entries}
