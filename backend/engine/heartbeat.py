"""
SK AgentCorp — Heartbeat Scheduler

The 24/7 heartbeat that keeps the company alive.
Periodically wakes up each active company, scans for work, and dispatches crews.

Uses APScheduler for reliable interval-based scheduling.
"""

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import get_settings
from backend.database import async_session
from backend.engine.anti_stuck import AntiStuckEngine
from backend.engine.crew_builder import CrewBuilder
from backend.services.audit_service import AuditService
from backend.services.company_service import CompanyService

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: AsyncIOScheduler | None = None


async def heartbeat_tick() -> None:
    """
    One heartbeat cycle. Called periodically by the scheduler.

    For each active company:
    1. Update heartbeat timestamp
    2. Run anti-stuck scan to recover stuck tasks/agents
    3. Process ready tasks via CrewBuilder
    4. Log results
    """
    logger.info("[Heartbeat] ♥ Tick")

    async with async_session() as db:
        try:
            company_service = CompanyService(db)
            companies = await company_service.list_all(active_only=True)

            for company in companies:
                if company.is_paused:
                    logger.debug(f"[Heartbeat] Skipping paused company: {company.name}")
                    continue

                logger.info(f"[Heartbeat] Processing company: {company.name}")

                try:
                    # 1. Update heartbeat
                    await company_service.update_heartbeat(company.id)

                    # 2. Anti-stuck scan
                    anti_stuck = AntiStuckEngine(db)
                    stuck_summary = await anti_stuck.scan_and_recover(company.id)

                    # 3. Process ready tasks
                    crew_builder = CrewBuilder(db)
                    crew_summary = await crew_builder.process_ready_tasks(company.id)

                    # 4. Log heartbeat
                    audit_service = AuditService(db)
                    await audit_service.log(
                        company_id=company.id,
                        event_type="heartbeat",
                        message=(
                            f"Heartbeat: {crew_summary.get('executed', 0)} tasks executed, "
                            f"{stuck_summary.get('retried', 0)} retried, "
                            f"{stuck_summary.get('failed_permanently', 0)} failed"
                        ),
                        category="system",
                    )

                except Exception as e:
                    logger.error(f"[Heartbeat] Error processing company {company.name}: {e}")

            await db.commit()

        except Exception as e:
            logger.error(f"[Heartbeat] Fatal error: {e}")
            await db.rollback()


def start_heartbeat() -> AsyncIOScheduler:
    """Start the heartbeat scheduler."""
    global _scheduler
    settings = get_settings()

    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        heartbeat_tick,
        "interval",
        seconds=settings.heartbeat_interval_seconds,
        id="sk_agentcorp_heartbeat",
        name="SK AgentCorp Company Heartbeat",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping heartbeats
    )
    _scheduler.start()
    logger.info(
        f"[Heartbeat] Started (interval: {settings.heartbeat_interval_seconds}s)"
    )
    return _scheduler


def stop_heartbeat() -> None:
    """Stop the heartbeat scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("[Heartbeat] Stopped")


async def trigger_heartbeat_now() -> dict:
    """Manually trigger a heartbeat (for testing/dashboard)."""
    logger.info("[Heartbeat] Manual trigger")
    await heartbeat_tick()
    return {"triggered_at": datetime.now(timezone.utc).isoformat()}
