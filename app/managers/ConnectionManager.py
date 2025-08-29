import logging
from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            logger.warning(f"Session {session_id} already has an active connection, closing old one")
            try:
                old_websocket = self.active_connections[session_id]
                await old_websocket.close(code=1000, reason="New connection")
            except Exception as e:
                logger.error(f"Error closing old connection for session {session_id}: {e}")
        
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"New WebSocket connection established for session: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket connection removed for session: {session_id}")

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                self.disconnect(session_id)
        else:
            logger.warning(f"No active connection for session {session_id}")

    def get_active_connections_count(self) -> int:
        return len(self.active_connections)

    def get_active_session_ids(self) -> list[str]:
        return list(self.active_connections.keys())