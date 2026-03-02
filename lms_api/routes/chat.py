from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import os
from datetime import datetime
from ..database import SessionLocal
from ..models import ChatMessage, ChatRoom, UserProfile, UserStatus, chat_room_members
from ..deps import get_db, get_current_user
from ..auth import decode_token

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: str, room_members: List[int]):
        for user_id in room_members:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(message)
                except:
                    pass

manager = ConnectionManager()

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, token: str):
    email = decode_token(token)
    if not email:
        await websocket.close(code=4001)
        return
    
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        await websocket.close(code=4001)
        db.close()
        return

    await manager.connect(user.id, websocket)
    
    # Update status to online
    status = db.query(UserStatus).filter(UserStatus.user_id == user.id).first()
    if not status:
        status = UserStatus(user_id=user.id, is_online=True, last_seen=datetime.utcnow())
        db.add(status)
    else:
        status.is_online = True
        status.last_seen = datetime.utcnow()
    db.commit()

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            msg = ChatMessage(
                room_id=room_id,
                sender_id=user.id,
                message=message_data.get("message", ""),
                file_url=message_data.get("file_url"),
                created_at=datetime.utcnow()
            )
            db.add(msg)
            db.commit()
            
            room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            if room:
                member_ids = [m.id for m in room.members]
                broadcast_data = {
                    "type": "message",
                    "room_id": room_id,
                    "sender_id": user.id,
                    "sender_name": user.name,
                    "message": msg.message,
                    "file_url": msg.file_url,
                    "created_at": msg.created_at.isoformat()
                }
                await manager.broadcast(json.dumps(broadcast_data), member_ids)
                
    except WebSocketDisconnect:
        manager.disconnect(user.id)
        status = db.query(UserStatus).filter(UserStatus.user_id == user.id).first()
        if status:
            status.is_online = False
            status.last_seen = datetime.utcnow()
            db.commit()
    finally:
        db.close()

@router.get("/chat/rooms/")
def list_rooms(user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    return user.chat_rooms

@router.post("/chat/rooms/")
def create_room(name: str, is_group: bool = False, member_ids: List[int] = [], user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    room = ChatRoom(name=name, is_group=is_group, created_at=datetime.utcnow())
    db.add(room)
    db.flush()
    
    # Add creator and members
    ids = list(set(member_ids + [user.id]))
    for uid in ids:
        u = db.query(UserProfile).filter(UserProfile.id == uid).first()
        if u:
            room.members.append(u)
    
    db.commit()
    db.refresh(room)
    return room

@router.get("/chat/rooms/{room_id}/messages/")
def get_messages(room_id: int, user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if user is member
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room or user not in room.members:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    return db.query(ChatMessage).filter(ChatMessage.room_id == room_id).order_by(ChatMessage.created_at.asc()).all()

@router.post("/chat/upload/")
async def upload_file(file: UploadFile = File(...), user: UserProfile = Depends(get_current_user)):
    # Simple local save for demo
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{datetime.now().timestamp()}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_url": f"/{file_path}"}
