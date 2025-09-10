from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set

router = APIRouter(tags=["Notifications"])


class VendorConnectionManager:
    def __init__(self) -> None:
        # vendor_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, vendor_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(vendor_id, set()).add(websocket)

    def disconnect(self, vendor_id: str, websocket: WebSocket):
        conns = self.active_connections.get(vendor_id)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                self.active_connections.pop(vendor_id, None)

    async def send_personal_json(self, vendor_id: str, data):
        for ws in list(self.active_connections.get(vendor_id, [])):
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(vendor_id, ws)

    async def broadcast_to_vendors(self, vendor_ids: Set[str], data):
        for vid in vendor_ids:
            await self.send_personal_json(vid, data)


manager = VendorConnectionManager()


@router.websocket("/ws/vendors/{vendor_id}")
async def vendor_ws(websocket: WebSocket, vendor_id: str):
    await manager.connect(vendor_id, websocket)
    try:
        while True:
            # Keep the connection alive; optionally echo pings
            _ = await websocket.receive_text()
            await websocket.send_text("ok")
    except WebSocketDisconnect:
        manager.disconnect(vendor_id, websocket)
