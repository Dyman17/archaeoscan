from typing import List
from fastapi import WebSocket

class NotificationsService:
    def __init__(self):
        self.websockets: List[WebSocket] = []
    
    def add_websocket(self, websocket: WebSocket):
        """Add WebSocket connection to notifications service"""
        self.websockets.append(websocket)
    
    def remove_websocket(self, websocket: WebSocket):
        """Remove WebSocket connection from notifications service"""
        if websocket in self.websockets:
            self.websockets.remove(websocket)
    
    async def broadcast_notification(self, message: str):
        """Broadcast notification to all connected WebSocket clients"""
        for websocket in self.websockets:
            try:
                await websocket.send_text(message)
            except:
                # Remove disconnected websockets
                self.remove_websocket(websocket)

# Global instance
notifications_service = NotificationsService()
