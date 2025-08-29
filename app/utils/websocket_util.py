from starlette.websockets import WebSocket

from app.managers import ConnectionManager


async def handle_websocket_disconnect(
        websocket: WebSocket,
        manager: ConnectionManager,
        session_id: str,
        error_message: str
) -> None:
    await websocket.send_json({"error": error_message})
    await manager.disconnect(session_id)
