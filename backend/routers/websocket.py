"""
SK AgentCorp — WebSocket Router

Real-time updates for the dashboard via native WebSocket.
Broadcasts agent status changes, task updates, and heartbeat events.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════
#  Connection Manager
# ═══════════════════════════════════════════════════════════════════════

class ConnectionManager:
    """Manages active WebSocket connections and broadcasts."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WS] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a message to all connected clients."""
        if not self.active_connections:
            return

        data = json.dumps(message, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)

        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send a message to a specific client."""
        data = json.dumps(message, default=str)
        await websocket.send_text(data)


# Singleton manager
manager = ConnectionManager()


# ═══════════════════════════════════════════════════════════════════════
#  WebSocket Endpoint
# ═══════════════════════════════════════════════════════════════════════

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time dashboard updates."""
    await manager.connect(websocket)

    # Send welcome message
    await manager.send_personal(websocket, {
        "type": "connected",
        "message": "Connected to SK AgentCorp real-time feed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    try:
        while True:
            # Listen for messages from client (ping/pong, commands)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                if msg_type == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ═══════════════════════════════════════════════════════════════════════
#  Broadcast Helpers (called by services/engine)
# ═══════════════════════════════════════════════════════════════════════

async def broadcast_event(event_type: str, data: dict[str, Any]) -> None:
    """Broadcast an event to all connected WebSocket clients."""
    await manager.broadcast({
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def broadcast_agent_update(agent_id: str, status: str, **kwargs: Any) -> None:
    """Broadcast an agent status change."""
    await broadcast_event("agent_update", {
        "agent_id": agent_id,
        "status": status,
        **kwargs,
    })


async def broadcast_task_update(task_id: str, status: str, **kwargs: Any) -> None:
    """Broadcast a task status change."""
    await broadcast_event("task_update", {
        "task_id": task_id,
        "status": status,
        **kwargs,
    })


async def broadcast_heartbeat(company_id: str, summary: dict) -> None:
    """Broadcast heartbeat results."""
    await broadcast_event("heartbeat", {
        "company_id": company_id,
        "summary": summary,
    })
